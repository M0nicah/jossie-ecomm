from rest_framework import serializers
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem, StockHistory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = ProductImageSerializer(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    has_discount = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description', 
            'price', 'original_price', 'category', 'category_name', 'sku',
            'stock_quantity', 'low_stock_threshold', 'is_active', 'is_featured',
            'weight', 'dimensions', 'created_at', 'updated_at', 'images',
            'primary_image', 'stock_status', 'has_discount', 'discount_percentage'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    primary_image = ProductImageSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    has_discount = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price', 'original_price',
            'category_name', 'stock_quantity', 'is_featured', 'primary_image',
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
    class Meta:
        model = Order
        fields = [
            'email', 'phone', 'first_name', 'last_name',
            'delivery_notes', 'notes'
        ]


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