from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem, StockHistory
from .serializers import (
    CategorySerializer, ProductSerializer, ProductListSerializer,
    CartSerializer, CartItemSerializer, OrderSerializer, OrderCreateSerializer,
    StockHistorySerializer
)
from .services import WhatsAppService, EmailService, OrderService
from .decorators import (
    admin_required, secure_admin_view, standard_admin_view, 
    rate_limit_admin, audit_log_admin, get_client_ip
)
from .auth_views import (
    track_admin_login_attempt,
    track_failed_admin_login,
    clear_failed_login_attempts,
    is_admin_account_locked,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        
        # Apply filters
        search = request.query_params.get('search', None)
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Sort options
        sort_by = request.query_params.get('sort', 'name')
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'newest':
            products = products.order_by('-created_at')
        else:
            products = products.order_by('name')
        
        serializer_context = self.get_serializer_context()
        serializer = ProductListSerializer(products, many=True, context=serializer_context)
        return Response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def list(self, request):
        queryset = self.get_queryset()
        
        # Apply filters
        category_id = request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) | 
                Q(category__name__icontains=search)
            )
        
        featured = request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Sort options
        sort_by = request.query_params.get('sort', '-created_at')
        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        # Get limit from query params, default to 8
        limit = int(request.query_params.get('limit', 8))
        
        # Ensure limit is reasonable (between 1 and 50)
        limit = max(1, min(limit, 50))
        
        # Get featured products with proper ordering
        featured_products = self.get_queryset().filter(
            is_featured=True
        ).order_by('-created_at')[:limit]
        
        serializer_context = self.get_serializer_context()
        serializer = ProductListSerializer(featured_products, many=True, context=serializer_context)
        return Response(serializer.data)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            return Cart.objects.filter(session_key=session_key)
    
    def get_or_create_cart(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            
            # Handle multiple carts with same session key (cleanup duplicates)
            carts = Cart.objects.filter(session_key=session_key)
            if carts.exists():
                cart = carts.first()
                # Delete any duplicates
                if carts.count() > 1:
                    carts.exclude(id=cart.id).delete()
            else:
                cart = Cart.objects.create(session_key=session_key)
        return cart
    
    def list(self, request):
        cart = self.get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_or_create_cart()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if product.stock_quantity < quantity:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            if product.stock_quantity < new_quantity:
                return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = new_quantity
            cart_item.save()
        
        serializer = CartItemSerializer(cart_item, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['put'])
    def update_item(self, request):
        cart = self.get_or_create_cart()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity'))
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        
        if quantity <= 0:
            cart_item.delete()
            return Response({'message': 'Item removed from cart'})
        
        if cart_item.product.stock_quantity < quantity:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = CartItemSerializer(cart_item, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        cart = self.get_or_create_cart()
        product_id = request.data.get('product_id')
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response({'message': 'Item removed from cart'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = self.get_or_create_cart()
        cart.items.all().delete()
        return Response({'message': 'Cart cleared'})


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related('items__product')
    serializer_class = OrderSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def create(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        whatsapp_url = WhatsAppService.generate_whatsapp_url(order)
        OrderService.process_new_order(order)

        response_data = OrderSerializer(order).data
        response_data['whatsapp_url'] = whatsapp_url
        response_data['whatsapp_number'] = settings.WHATSAPP_BUSINESS_NUMBER

        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class StockHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockHistory.objects.all().select_related('product', 'user')
    serializer_class = StockHistorySerializer
    permission_classes = [permissions.IsAdminUser]


def home(request):
    return render(request, 'core/home.html')

def products(request):
    # Get all active products with related data
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    
    # Get all categories for filter dropdown
    categories = Category.objects.filter(is_active=True)
    
    # Apply filters from GET parameters
    category_id = request.GET.get('category')
    if category_id:
        try:
            queryset = queryset.filter(category_id=int(category_id))
        except (ValueError, TypeError):
            pass
    
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) | 
            Q(category__name__icontains=search)
        )
    
    featured = request.GET.get('featured')
    if featured == 'true':
        queryset = queryset.filter(is_featured=True)
    
    # Sort options
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price_low':
        queryset = queryset.order_by('price')
    elif sort_by == 'price_high':
        queryset = queryset.order_by('-price')
    elif sort_by == 'name':
        queryset = queryset.order_by('name')
    else:
        queryset = queryset.order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    context = {
        'products': products_page,
        'categories': categories,
        'current_filters': {
            'category': category_id,
            'search': search,
            'featured': featured,
            'sort': sort_by,
        },
        'total_products': queryset.count(),
    }
    
    return render(request, 'core/products.html', context)

def product_detail(request, slug):
    return render(request, 'core/product_detail.html', {'slug': slug})

def category(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    return render(request, 'core/category.html', {'category': category})

def cart(request):
    return render(request, 'core/cart.html')

def about(request):
    return render(request, 'core/about.html')

def faq(request):
    return render(request, 'core/faq.html')

def contact(request):
    return render(request, 'core/contact.html')

@require_http_methods(["GET", "POST"])
@csrf_protect
@ensure_csrf_cookie
@rate_limit_admin(max_attempts=5, window_minutes=15)
@audit_log_admin(action="admin_login_page_access", sensitive=True)
def admin_login(request):
    """Secure admin login page with rate limiting and audit logging"""
    error_message = None
    client_ip = get_client_ip(request)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            error_message = 'Username and password are required.'
        else:
            track_admin_login_attempt(client_ip, username, request)
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.is_superuser and user.is_active:
                if is_admin_account_locked(username):
                    error_message = 'Account temporarily locked due to security policy.'
                else:
                    now_iso = timezone.now().isoformat()
                    login(request, user)
                    request.session['admin_session_start'] = now_iso
                    request.session['last_activity'] = now_iso
                    request.session['login_ip'] = client_ip
                    request.session['is_admin_session'] = True
                    clear_failed_login_attempts(client_ip, username)
                    return redirect('admin_dashboard')
            else:
                track_failed_admin_login(client_ip, username)
                error_message = 'Invalid credentials or insufficient permissions.'
    
    context = {
        'error_message': error_message,
    }
    return render(request, 'core/admin_login.html', context)

@standard_admin_view
def admin_dashboard(request):
    """Secure admin dashboard with comprehensive security protection"""
    return render(request, 'core/admin_dashboard.html')
