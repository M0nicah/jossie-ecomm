from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
import json
import uuid

from .models import (
    Category, Product, ProductImage, Cart, CartItem, 
    Order, OrderItem, StockHistory, AdminUser
)
from .services import WhatsAppService, EmailService, OrderService, InventoryService


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
            description="Electronic items"
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Electronics")
        self.assertEqual(self.category.slug, "electronics")
        self.assertTrue(self.category.is_active)

    def test_category_str(self):
        self.assertEqual(str(self.category), "Electronics")

    def test_unique_slug(self):
        with self.assertRaises(Exception):
            Category.objects.create(
                name="Electronics 2",
                slug="electronics"
            )


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics"
        )
        self.product = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            original_price=Decimal('30000.00'),
            category=self.category,
            sku="PHONE001",
            stock_quantity=10,
            low_stock_threshold=5
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Smartphone")
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.stock_quantity, 10)

    def test_stock_status_in_stock(self):
        self.assertEqual(self.product.stock_status, 'in_stock')

    def test_stock_status_low_stock(self):
        self.product.stock_quantity = 3
        self.assertEqual(self.product.stock_status, 'low_stock')

    def test_stock_status_out_of_stock(self):
        self.product.stock_quantity = 0
        self.assertEqual(self.product.stock_status, 'out_of_stock')

    def test_has_discount(self):
        self.assertTrue(self.product.has_discount)

    def test_discount_percentage(self):
        self.assertEqual(self.product.discount_percentage, 17)

    def test_no_discount(self):
        product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            description="Test",
            price=Decimal('100.00'),
            category=self.category,
            sku="TEST001"
        )
        self.assertFalse(product.has_discount)
        self.assertEqual(product.discount_percentage, 0)


class ProductImageModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test", slug="test")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            description="Test",
            price=Decimal('100.00'),
            category=self.category,
            sku="TEST001"
        )

    def test_primary_image_uniqueness(self):
        # Create first primary image
        image1 = ProductImage.objects.create(
            product=self.product,
            image="test1.jpg",
            is_primary=True
        )
        
        # Create second primary image - should make first one non-primary
        image2 = ProductImage.objects.create(
            product=self.product,
            image="test2.jpg",
            is_primary=True
        )
        
        image1.refresh_from_db()
        self.assertFalse(image1.is_primary)
        self.assertTrue(image2.is_primary)


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Test", slug="test")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            description="Test",
            price=Decimal('100.00'),
            category=self.category,
            sku="TEST001",
            stock_quantity=10
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)
        self.assertIsNone(self.cart.session_key)

    def test_cart_str_with_user(self):
        self.assertEqual(str(self.cart), f"Cart for {self.user.username}")

    def test_cart_str_anonymous(self):
        cart = Cart.objects.create(session_key="test123")
        self.assertEqual(str(cart), "Anonymous Cart test123")

    def test_total_items_empty(self):
        self.assertEqual(self.cart.total_items, 0)

    def test_total_price_empty(self):
        self.assertEqual(self.cart.total_price, 0)

    def test_total_items_with_items(self):
        # Create another product to avoid unique constraint
        product2 = Product.objects.create(
            name="Test Product 2",
            slug="test-product-2",
            description="Test",
            price=Decimal('150.00'),
            category=self.category,
            sku="TEST002",
            stock_quantity=10
        )
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        CartItem.objects.create(cart=self.cart, product=product2, quantity=3)
        self.assertEqual(self.cart.total_items, 5)

    def test_total_price_with_items(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(self.cart.total_price, Decimal('200.00'))


class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.category = Category.objects.create(name="Test", slug="test")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            description="Test",
            price=Decimal('50.00'),
            category=self.category,
            sku="TEST001"
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )

    def test_cart_item_creation(self):
        self.assertEqual(self.cart_item.quantity, 3)
        self.assertEqual(self.cart_item.product, self.product)

    def test_total_price(self):
        self.assertEqual(self.cart_item.total_price, Decimal('150.00'))

    def test_cart_item_str(self):
        self.assertEqual(str(self.cart_item), "Test Product x 3")

    def test_unique_cart_product_constraint(self):
        with self.assertRaises(Exception):
            CartItem.objects.create(
                cart=self.cart,
                product=self.product,
                quantity=1
            )


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.order = Order.objects.create(
            user=self.user,
            email="test@example.com",
            phone="1234567890",
            first_name="John",
            last_name="Doe",
            total_amount=Decimal('500.00'),
            subtotal_amount=Decimal('450.00'),
            shipping_fee=Decimal('50.00')
        )

    def test_order_creation(self):
        self.assertEqual(self.order.email, "test@example.com")
        self.assertEqual(self.order.status, 'pending')
        self.assertIsInstance(self.order.order_id, uuid.UUID)

    def test_full_name_property(self):
        self.assertEqual(self.order.full_name, "John Doe")

    def test_order_str(self):
        expected = f"Order {self.order.order_id} - pending"
        self.assertEqual(str(self.order), expected)


class OrderItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.category = Category.objects.create(name="Test", slug="test")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            description="Test",
            price=Decimal('100.00'),
            category=self.category,
            sku="TEST001"
        )
        self.order = Order.objects.create(
            user=self.user,
            email="test@example.com",
            phone="1234567890",
            first_name="John",
            last_name="Doe",
            total_amount=Decimal('500.00')
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name="Test Product",
            product_price=Decimal('100.00'),
            quantity=2
        )

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.product_name, "Test Product")

    def test_total_price(self):
        self.assertEqual(self.order_item.total_price, Decimal('200.00'))

    def test_order_item_str(self):
        self.assertEqual(str(self.order_item), "Test Product x 2")


class StockHistoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.category = Category.objects.create(name="Test", slug="test")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            description="Test",
            price=Decimal('100.00'),
            category=self.category,
            sku="TEST001",
            stock_quantity=10
        )
        self.stock_history = StockHistory.objects.create(
            product=self.product,
            transaction_type='sale',
            quantity_change=-2,
            previous_stock=10,
            new_stock=8,
            reason="Test sale",
            user=self.user
        )

    def test_stock_history_creation(self):
        self.assertEqual(self.stock_history.transaction_type, 'sale')
        self.assertEqual(self.stock_history.quantity_change, -2)
        self.assertEqual(self.stock_history.new_stock, 8)

    def test_stock_history_str(self):
        expected = f"{self.product.name} - sale (-2)"
        self.assertEqual(str(self.stock_history), expected)


class AdminUserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("admin", "admin@example.com", "pass")
        self.admin_user = AdminUser.objects.create(
            user=self.user,
            phone="1234567890"
        )

    def test_admin_user_creation(self):
        self.assertEqual(self.admin_user.user, self.user)
        self.assertTrue(self.admin_user.is_active)

    def test_admin_user_str(self):
        expected = f"Admin: {self.user.username}"
        self.assertEqual(str(self.admin_user), expected)


# API Tests
class CategoryAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
            description="Electronic items"
        )
        self.product = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            category=self.category,
            sku="PHONE001",
            stock_quantity=10
        )

    def test_list_categories(self):
        url = '/api/categories/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_category_products(self):
        url = f'/api/categories/{self.category.id}/products/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_category_products_with_search(self):
        url = f'/api/categories/{self.category.id}/products/?search=phone'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class ProductAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product1 = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            category=self.category,
            sku="PHONE001",
            stock_quantity=10,
            is_featured=True
        )
        self.product2 = Product.objects.create(
            name="Laptop",
            slug="laptop",
            description="Gaming laptop",
            price=Decimal('80000.00'),
            category=self.category,
            sku="LAPTOP001",
            stock_quantity=5
        )

    def test_list_products(self):
        url = '/api/products/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_product_detail(self):
        url = f'/api/products/{self.product1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Smartphone')

    def test_featured_products(self):
        url = '/api/products/featured/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_category(self):
        url = f'/api/products/?category={self.category.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_search_products(self):
        url = '/api/products/?search=phone'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_sort_by_price_low(self):
        url = '/api/products/?sort=price_low'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], 'Smartphone')


class CartAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            category=self.category,
            sku="PHONE001",
            stock_quantity=10
        )
    
    def tearDown(self):
        # Clean up carts after each test to avoid conflicts
        Cart.objects.all().delete()

    def test_get_cart_anonymous(self):
        url = '/api/cart/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 0)

    def test_get_cart_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/cart/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_item_to_cart(self):
        url = '/api/cart/add_item/'
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 2)

    def test_add_item_insufficient_stock(self):
        url = '/api/cart/add_item/'
        data = {
            'product_id': self.product.id,
            'quantity': 15  # More than available stock
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_nonexistent_product(self):
        url = '/api/cart/add_item/'
        data = {
            'product_id': 999,
            'quantity': 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_cart_item(self):
        # Use a fresh client to avoid session conflicts
        fresh_client = APIClient()
        
        # First add an item to cart using the API
        url = '/api/cart/add_item/'
        data = {
            'product_id': self.product.id,
            'quantity': 1
        }
        fresh_client.post(url, data)
        
        # Now update it
        url = '/api/cart/update_item/'
        data = {
            'product_id': self.product.id,
            'quantity': 3
        }
        response = fresh_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_cart_item(self):
        # Use a fresh client to avoid session conflicts
        fresh_client = APIClient()
        
        # First add an item to cart using the API
        url = '/api/cart/add_item/'
        data = {
            'product_id': self.product.id,
            'quantity': 1
        }
        fresh_client.post(url, data)
        
        # Now remove it
        url = '/api/cart/remove_item/'
        data = {'product_id': self.product.id}
        response = fresh_client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_clear_cart(self):
        url = '/api/cart/clear/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OrderAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.admin_user = User.objects.create_superuser("admin", "admin@example.com", "pass")
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            category=self.category,
            sku="PHONE001",
            stock_quantity=10
        )
    
    def tearDown(self):
        # Clean up carts after each test to avoid conflicts
        Cart.objects.all().delete()

    def test_create_order_with_cart(self):
        # Use a fresh client to avoid session conflicts
        fresh_client = APIClient()
        
        # First add items to cart using the API
        url = '/api/cart/add_item/'
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        fresh_client.post(url, data)
        
        # Now create order
        url = '/api/orders/'
        data = {
            'email': 'customer@example.com',
            'phone': '1234567890',
            'first_name': 'John',
            'last_name': 'Doe',
            'delivery_notes': 'Please deliver to front door',
            'subtotal_amount': '50000.00'
        }
        response = fresh_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_order_empty_cart(self):
        url = '/api/orders/'
        data = {
            'email': 'customer@example.com',
            'phone': '1234567890',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_requires_admin(self):
        url = '/api/orders/'
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_list_orders_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = '/api/orders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_order_status(self):
        self.client.force_authenticate(user=self.admin_user)
        order = Order.objects.create(
            email='test@example.com',
            phone='1234567890',
            first_name='John',
            last_name='Doe',
            total_amount=Decimal('25000.00')
        )
        
        url = f'/api/orders/{order.id}/update_status/'
        data = {'status': 'confirmed'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'confirmed')


class StockHistoryAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser("admin", "admin@example.com", "pass")
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            category=self.category,
            sku="PHONE001",
            stock_quantity=10
        )

    def test_stock_history_requires_admin(self):
        url = '/api/stock-history/'
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_stock_history_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        
        # Create stock history record
        StockHistory.objects.create(
            product=self.product,
            transaction_type='sale',
            quantity_change=-2,
            previous_stock=10,
            new_stock=8,
            reason="Test sale"
        )
        
        url = '/api/stock-history/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


# Service Layer Tests
class WhatsAppServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            category=self.category,
            sku="PHONE001",
            stock_quantity=10
        )
        self.order = Order.objects.create(
            user=self.user,
            email="test@example.com",
            phone="1234567890",
            first_name="John",
            last_name="Doe",
            total_amount=Decimal('25450.00'),
            subtotal_amount=Decimal('25000.00'),
            shipping_fee=Decimal('450.00'),
            delivery_notes="Test delivery"
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            product_price=self.product.price,
            quantity=1
        )

    def test_generate_order_message(self):
        message = WhatsAppService.generate_order_message(self.order)
        self.assertIn("Order summary:", message)
        self.assertIn("John Doe", message)
        self.assertIn("Smartphone", message)
        self.assertIn("KES 25,000", message)
        self.assertIn("Total payable: KES 25,450", message)
        self.assertNotIn("🛍️", message)
        self.assertNotIn("🙏", message)

    def test_generate_whatsapp_url(self):
        url = WhatsAppService.generate_whatsapp_url(self.order)
        self.assertTrue(url.startswith("https://wa.me/"))
        self.assertIn("text=", url)

    def test_generate_admin_notification_message(self):
        message = WhatsAppService.generate_admin_notification_message(self.order)
        self.assertIn("New Order Alert!", message)
        self.assertIn("John Doe", message)
        self.assertIn("KES 25,450", message)

    def test_generate_admin_whatsapp_url(self):
        url = WhatsAppService.generate_admin_whatsapp_url(self.order)
        self.assertTrue(url.startswith("https://wa.me/"))


class EmailServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            category=self.category,
            sku="PHONE001"
        )
        self.order = Order.objects.create(
            user=self.user,
            email="test@example.com",
            phone="1234567890",
            first_name="John",
            last_name="Doe",
            total_amount=Decimal('25000.00')
        )

    def test_send_order_confirmation(self):
        # This will use console backend in test
        result = EmailService.send_order_confirmation(self.order)
        self.assertTrue(result)

    def test_send_admin_notification(self):
        # This will use console backend in test
        result = EmailService.send_admin_notification(self.order)
        self.assertTrue(result)


class OrderServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            category=self.category,
            sku="PHONE001"
        )
        self.order = Order.objects.create(
            user=self.user,
            email="test@example.com",
            phone="1234567890",
            first_name="John",
            last_name="Doe",
            total_amount=Decimal('25000.00')
        )

    def test_process_new_order(self):
        result = OrderService.process_new_order(self.order)
        self.assertTrue(result)
        
        # Check that whatsapp_sent was marked as True
        self.order.refresh_from_db()
        self.assertTrue(self.order.whatsapp_sent)

    def test_get_order_analytics(self):
        analytics = OrderService.get_order_analytics()
        
        self.assertIn('total_orders', analytics)
        self.assertIn('total_revenue', analytics)
        self.assertIn('orders_today', analytics)
        self.assertIn('orders_this_week', analytics)
        self.assertIn('orders_this_month', analytics)
        self.assertIn('revenue_this_month', analytics)
        self.assertIn('pending_orders', analytics)
        self.assertIn('confirmed_orders', analytics)
        self.assertIn('status_breakdown', analytics)
        
        self.assertEqual(analytics['total_orders'], 1)
        self.assertEqual(analytics['pending_orders'], 1)


class InventoryServiceTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product_in_stock = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            category=self.category,
            sku="PHONE001",
            stock_quantity=15,
            low_stock_threshold=10
        )
        self.product_low_stock = Product.objects.create(
            name="Tablet",
            slug="tablet",
            description="Latest tablet",
            price=Decimal('35000.00'),
            category=self.category,
            sku="TABLET001",
            stock_quantity=5,
            low_stock_threshold=10
        )
        self.product_out_of_stock = Product.objects.create(
            name="Laptop",
            slug="laptop",
            description="Gaming laptop",
            price=Decimal('80000.00'),
            category=self.category,
            sku="LAPTOP001",
            stock_quantity=0,
            low_stock_threshold=5
        )

    def test_get_low_stock_products(self):
        low_stock = InventoryService.get_low_stock_products()
        self.assertEqual(low_stock.count(), 2)  # tablet and laptop
        
        product_names = [p.name for p in low_stock]
        self.assertIn("Tablet", product_names)
        self.assertIn("Laptop", product_names)
        self.assertNotIn("Smartphone", product_names)

    def test_get_inventory_alerts(self):
        alerts = InventoryService.get_inventory_alerts()
        
        self.assertEqual(alerts['low_stock_count'], 2)
        self.assertEqual(alerts['out_of_stock_count'], 1)
        self.assertEqual(alerts['total_alerts'], 3)


# Template View Tests
class TemplateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
            description="Electronic items"
        )
        self.product = Product.objects.create(
            name="Smartphone",
            slug="smartphone",
            description="Latest smartphone",
            price=Decimal('25000.00'),
            category=self.category,
            sku="PHONE001",
            stock_quantity=10
        )
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )

    def test_home_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_products_view(self):
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/products.html')

    def test_products_view_with_category_filter(self):
        response = self.client.get(f'/products/?category={self.category.id}')
        self.assertEqual(response.status_code, 200)

    def test_products_view_with_search(self):
        response = self.client.get('/products/?search=phone')
        self.assertEqual(response.status_code, 200)

    def test_products_view_with_featured_filter(self):
        response = self.client.get('/products/?featured=true')
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view(self):
        response = self.client.get(f'/products/{self.product.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/product_detail.html')

    def test_category_view(self):
        response = self.client.get(f'/category/{self.category.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/category.html')

    def test_cart_view(self):
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/cart.html')

    def test_about_view(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')

    def test_faq_view(self):
        response = self.client.get('/faq/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/faq.html')

    def test_contact_view(self):
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contact.html')

    def test_admin_login_view(self):
        response = self.client.get('/admin-login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/admin_login.html')

    def test_admin_dashboard_view(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/admin_dashboard.html')
