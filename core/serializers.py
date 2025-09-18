from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem, StockHistory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'optimized_image', 'alt_text', 'is_primary', 'order']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = ProductImageSerializer(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    has_discount = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    primary_image_url = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description', 
            'price', 'original_price', 'category', 'category_name', 'sku',
            'stock_quantity', 'low_stock_threshold', 'is_active', 'is_featured',
            'weight', 'dimensions', 'created_at', 'updated_at', 'images',
            'primary_image', 'primary_image_url', 'stock_status', 'has_discount', 'discount_percentage'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    primary_image = ProductImageSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    has_discount = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    primary_image_url = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price', 'original_price',
            'category_name', 'stock_quantity', 'is_featured', 'primary_image', 'primary_image_url',
            'stock_status', 'has_discount', 'discount_percentage'
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price', 'created_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'email', 'phone', 'first_name', 'last_name',
            'full_name', 'delivery_notes', 'status', 'subtotal_amount',
            'shipping_fee', 'total_amount', 'total_items', 'notes', 'whatsapp_sent',
            'created_at', 'updated_at', 'items'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    cart = None

    class Meta:
        model = Order
        fields = [
            'email', 'phone', 'first_name', 'last_name',
            'delivery_notes', 'notes'
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError('Request context is required.')

        cart = self._get_cart(request)
        if cart is None or not cart.items.exists():
            raise serializers.ValidationError({'cart': 'Cart is empty.'})

        for item in cart.items.select_related('product'):
            if item.product.stock_quantity < item.quantity:
                raise serializers.ValidationError({
                    'cart': f"Insufficient stock for {item.product.name}"
                })

        attrs['cart'] = cart
        return attrs

    def create(self, validated_data):
        cart = validated_data.pop('cart')
        request = self.context['request']
        user = request.user if request.user.is_authenticated else None

        shipping_field = Order._meta.get_field('shipping_fee')
        shipping_default = shipping_field.get_default() if hasattr(shipping_field, 'get_default') else shipping_field.default
        shipping_fee = Decimal(str(shipping_default or 0))
        subtotal = Decimal(str(cart.total_price))

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                shipping_fee=shipping_fee,
                subtotal_amount=subtotal,
                total_amount=subtotal + shipping_fee,
                **validated_data
            )

            order_items = []
            stock_history_entries = []

            for item in cart.items.select_related('product'):
                product = item.product
                previous_stock = product.stock_quantity
                product.stock_quantity = max(0, previous_stock - item.quantity)
                product.save(update_fields=['stock_quantity'])

                order_items.append(OrderItem(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_price=product.price,
                    quantity=item.quantity
                ))

                stock_history_entries.append(StockHistory(
                    product=product,
                    transaction_type='sale',
                    quantity_change=-item.quantity,
                    previous_stock=previous_stock,
                    new_stock=product.stock_quantity,
                    reason=f'Order {order.order_id}',
                    order=order
                ))

            if order_items:
                OrderItem.objects.bulk_create(order_items)
            if stock_history_entries:
                StockHistory.objects.bulk_create(stock_history_entries)

            cart.items.all().delete()

        return order

    def _get_cart(self, request):
        if request.user.is_authenticated:
            return Cart.objects.filter(user=request.user).prefetch_related('items__product').first()

        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        return Cart.objects.filter(session_key=session_key).prefetch_related('items__product').first()


class StockHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = StockHistory
        fields = [
            'id', 'product', 'product_name', 'transaction_type',
            'quantity_change', 'previous_stock', 'new_stock', 'reason',
            'user_name', 'created_at'
        ]
