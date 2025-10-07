from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auth_views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet)
router.register(r'stock-history', views.StockHistoryViewSet)

urlpatterns = [
    # Frontend views
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('cart/', views.cart, name='cart'),
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # Authentication APIs
    path('api/auth/register/', auth_views.register_view, name='api_register'),
    path('api/auth/login/', auth_views.login_view, name='api_login'),
    path('api/auth/logout/', auth_views.logout_view, name='api_logout'),
    path('api/auth/user/', auth_views.current_user_view, name='api_current_user'),
    
    # Admin Authentication
    path('admin/api/login/', auth_views.admin_login_view, name='admin_login_api'),
    path('admin/api/logout/', auth_views.admin_logout_view, name='admin_logout_api'),
]