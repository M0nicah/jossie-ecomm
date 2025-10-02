from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import logging
from datetime import datetime, timedelta
from .decorators import rate_limit_admin, audit_log_admin, get_client_ip

logger = logging.getLogger('security')


@csrf_protect
@never_cache
@require_http_methods(["POST"])
@rate_limit_admin(max_attempts=5, window_minutes=15, block_minutes=15)
@audit_log_admin(action="admin_login", sensitive=True)
def admin_login_view(request):
    """Secure admin login view with comprehensive security features"""
    client_ip = get_client_ip(request)
    
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Input validation
        if not username or not password:
            logger.warning(f"Admin login attempt with missing credentials from {client_ip}")
            return JsonResponse({
                'success': False,
                'message': 'Username and password are required'
            }, status=400)
        
        # Additional security: Check for common attack patterns
        if len(username) > 150 or len(password) > 128:
            logger.warning(f"Admin login attempt with unusually long credentials from {client_ip}")
            return JsonResponse({
                'success': False,
                'message': 'Invalid credentials'
            }, status=400)
        
        # Track login attempt
        track_admin_login_attempt(client_ip, username, request)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser and user.is_active:
            # Check if account is locked (additional security measure)
            if is_admin_account_locked(username):
                logger.critical(f"Login attempt for locked admin account {username} from {client_ip}")
                return JsonResponse({
                    'success': False,
                    'message': 'Account temporarily locked due to security policy'
                }, status=423)
            
            # Successful login
            login(request, user)
            
            # Set secure session data
            request.session['admin_session_start'] = timezone.now().isoformat()
            request.session['last_activity'] = timezone.now().isoformat()
            request.session['login_ip'] = client_ip
            request.session['is_admin_session'] = True
            
            # Clear failed login attempts
            clear_failed_login_attempts(client_ip, username)
            
            # Log successful login
            logger.info(f"Successful admin login for {username} from {client_ip}")
            
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'redirect_url': '/admin-dashboard/',
                'session_timeout': 4 * 60 * 60  # 4 hours in seconds
            })
        else:
            # Failed login
            failed_reason = "invalid_credentials"
            if user is not None:
                if not user.is_superuser:
                    failed_reason = "insufficient_permissions"
                elif not user.is_active:
                    failed_reason = "inactive_account"
            
            logger.warning(
                f"Failed admin login attempt for {username} from {client_ip} - "
                f"Reason: {failed_reason}"
            )
            
            # Track failed attempt
            track_failed_admin_login(client_ip, username)
            
            return JsonResponse({
                'success': False,
                'message': 'Invalid credentials or insufficient permissions'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred during login'
        }, status=500)


@csrf_protect
@never_cache
@require_http_methods(["POST", "GET"])
@audit_log_admin(action="admin_logout", sensitive=False)
def admin_logout_view(request):
    """Secure admin logout view"""
    client_ip = get_client_ip(request)
    username = getattr(request.user, 'username', 'Unknown')
    
    if request.user.is_authenticated:
        logger.info(f"Admin logout for {username} from {client_ip}")
        
        # Clear sensitive session data
        sensitive_keys = ['admin_session_start', 'last_activity', 'login_ip', 'is_admin_session']
        for key in sensitive_keys:
            request.session.pop(key, None)
    
    logout(request)
    
    return JsonResponse({
        'success': True,
        'message': 'Logged out successfully',
        'redirect_url': '/admin-login/'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """User registration endpoint"""
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        # Validation
        if not username or not email or not password:
            return Response({
                'success': False,
                'message': 'Username, email, and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'message': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': 'Email already registered'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        return Response({
            'success': True,
            'message': 'Registration successful',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred during registration'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'success': False,
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        else:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred during login'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def logout_view(request):
    """User logout endpoint"""
    logout(request)
    return Response({
        'success': True,
        'message': 'Logged out successfully'
    })


@api_view(['GET'])
def current_user_view(request):
    """Get current user information"""
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser
            }
        })
    else:
        return Response({
            'authenticated': False,
            'user': None
        })


# Security utility functions for admin authentication

def track_admin_login_attempt(ip, username, request):
    """Track admin login attempts for security monitoring"""
    timestamp = timezone.now().isoformat()
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')[:200]
    
    # Store attempt in cache for monitoring
    attempt_key = f"admin_login_attempt:{ip}:{username}"
    attempts = cache.get(attempt_key, [])
    attempts.append({
        'timestamp': timestamp,
        'user_agent': user_agent,
        'path': request.path
    })
    
    # Keep only last 10 attempts per IP/username combo
    attempts = attempts[-10:]
    cache.set(attempt_key, attempts, timeout=3600)  # 1 hour


def track_failed_admin_login(ip, username):
    """Track failed admin login attempts"""
    timestamp = timezone.now().isoformat()
    
    # Track by IP
    ip_key = f"failed_admin_login_ip:{ip}"
    ip_attempts = cache.get(ip_key, [])
    ip_attempts.append({'username': username, 'timestamp': timestamp})
    ip_attempts = ip_attempts[-20:]  # Keep last 20 attempts per IP
    cache.set(ip_key, ip_attempts, timeout=7200)  # 2 hours
    
    # Track by username
    user_key = f"failed_admin_login_user:{username}"
    user_attempts = cache.get(user_key, [])
    user_attempts.append({'ip': ip, 'timestamp': timestamp})
    user_attempts = user_attempts[-10:]  # Keep last 10 attempts per username
    cache.set(user_key, user_attempts, timeout=3600)  # 1 hour
    
    # Check for account locking
    if len(user_attempts) >= 5:
        # Lock account for 1 hour if 5 failed attempts in last hour
        lock_key = f"admin_account_lock:{username}"
        cache.set(lock_key, True, timeout=3600)
        logger.critical(f"Admin account {username} locked due to repeated failed login attempts")


def clear_failed_login_attempts(ip, username):
    """Clear failed login attempts after successful login"""
    ip_key = f"failed_admin_login_ip:{ip}"
    user_key = f"failed_admin_login_user:{username}"
    lock_key = f"admin_account_lock:{username}"
    
    cache.delete(ip_key)
    cache.delete(user_key)
    cache.delete(lock_key)


def is_admin_account_locked(username):
    """Check if admin account is locked"""
    lock_key = f"admin_account_lock:{username}"
    return cache.get(lock_key, False)