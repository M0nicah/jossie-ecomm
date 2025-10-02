from functools import wraps
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
import logging
import json
from datetime import datetime, timedelta
from ipaddress import ip_address, ip_network

logger = logging.getLogger('security')


def admin_required(view_func=None, *, redirect_to='admin_login', json_response=False):
    """
    Decorator to require admin authentication
    
    Args:
        redirect_to: URL name to redirect to if not authenticated
        json_response: Return JSON response instead of redirect
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if user is authenticated and is admin
            if not (request.user.is_authenticated and 
                   request.user.is_superuser and 
                   request.user.is_active):
                
                # Log unauthorized access attempt
                client_ip = get_client_ip(request)
                logger.warning(
                    f"Unauthorized admin access attempt from {client_ip} "
                    f"to {request.path} - User: {getattr(request.user, 'username', 'Anonymous')}"
                )
                
                if json_response or request.content_type == 'application/json' or 'api/' in request.path:
                    return JsonResponse({
                        'success': False,
                        'message': 'Admin authentication required',
                        'redirect_url': f'/{redirect_to}/'
                    }, status=401)
                else:
                    messages.error(request, 'Admin access required. Please login.')
                    return redirect(redirect_to)
            
            # Log successful admin access
            client_ip = get_client_ip(request)
            logger.info(
                f"Admin access granted to {request.user.username} from {client_ip} "
                f"for {request.path}"
            )
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if view_func is None:
        return decorator
    else:
        return decorator(view_func)


def rate_limit_admin(max_attempts=5, window_minutes=15, block_minutes=15):
    """
    Rate limiting decorator for admin endpoints
    
    Args:
        max_attempts: Maximum attempts allowed
        window_minutes: Time window for counting attempts
        block_minutes: How long to block after exceeding limit
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            cache_key = f"rate_limit_admin:{view_func.__name__}:{client_ip}"
            
            # Get current attempts
            attempts_data = cache.get(cache_key, {'attempts': 0, 'first_attempt': None})
            
            current_time = timezone.now()
            
            # Reset counter if window has passed
            if attempts_data['first_attempt']:
                first_attempt_time = datetime.fromisoformat(attempts_data['first_attempt'].replace('Z', '+00:00'))
                if timezone.is_naive(first_attempt_time):
                    first_attempt_time = timezone.make_aware(first_attempt_time)
                
                if current_time - first_attempt_time > timedelta(minutes=window_minutes):
                    attempts_data = {'attempts': 0, 'first_attempt': None}
            
            # Check if rate limited
            if attempts_data['attempts'] >= max_attempts:
                logger.warning(f"Rate limit exceeded for {client_ip} on {view_func.__name__}")
                
                if request.content_type == 'application/json' or 'api/' in request.path:
                    return JsonResponse({
                        'success': False,
                        'message': f'Rate limit exceeded. Try again in {block_minutes} minutes.',
                        'retry_after': block_minutes * 60
                    }, status=429)
                else:
                    return HttpResponseForbidden(
                        f"Too many attempts. Please try again in {block_minutes} minutes."
                    )
            
            # Execute the view
            try:
                response = view_func(request, *args, **kwargs)
                
                # Only count failed attempts (non-2xx responses)
                if hasattr(response, 'status_code') and response.status_code >= 400:
                    attempts_data['attempts'] += 1
                    if attempts_data['first_attempt'] is None:
                        attempts_data['first_attempt'] = current_time.isoformat()
                    
                    cache.set(cache_key, attempts_data, timeout=block_minutes * 60)
                
                return response
                
            except Exception as e:
                # Count exceptions as failed attempts
                attempts_data['attempts'] += 1
                if attempts_data['first_attempt'] is None:
                    attempts_data['first_attempt'] = current_time.isoformat()
                
                cache.set(cache_key, attempts_data, timeout=block_minutes * 60)
                raise e
                
        return _wrapped_view
    return decorator


def ip_whitelist_required(allowed_ips=None):
    """
    Decorator to restrict access to whitelisted IPs only
    
    Args:
        allowed_ips: List of allowed IPs/CIDR blocks. If None, uses settings.ADMIN_ALLOWED_IPS
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            
            # Get allowed IPs
            whitelist = allowed_ips or getattr(settings, 'ADMIN_ALLOWED_IPS', [])
            
            # If no whitelist configured, allow all
            if not whitelist:
                return view_func(request, *args, **kwargs)
            
            # Check if IP is allowed
            if not is_ip_allowed(client_ip, whitelist):
                logger.critical(
                    f"Blocked admin access from non-whitelisted IP: {client_ip} "
                    f"to {request.path} - User: {getattr(request.user, 'username', 'Anonymous')}"
                )
                
                if request.content_type == 'application/json' or 'api/' in request.path:
                    return JsonResponse({
                        'success': False,
                        'message': 'Access denied from your IP address'
                    }, status=403)
                else:
                    return HttpResponseForbidden("Access denied from your IP address")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def audit_log_admin(action=None, sensitive=False):
    """
    Decorator to audit log admin actions
    
    Args:
        action: Custom action name (defaults to view function name)
        sensitive: Whether this is a sensitive action requiring detailed logging
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            action_name = action or view_func.__name__
            start_time = timezone.now()
            
            # Pre-action logging
            if sensitive:
                logger.info(
                    f"SENSITIVE ADMIN ACTION START - "
                    f"Action: {action_name}, "
                    f"User: {getattr(request.user, 'username', 'Anonymous')}, "
                    f"IP: {client_ip}, "
                    f"Path: {request.path}, "
                    f"Method: {request.method}"
                )
            
            try:
                # Execute the view
                response = view_func(request, *args, **kwargs)
                
                # Post-action logging
                duration = (timezone.now() - start_time).total_seconds()
                
                log_level = logger.info if not sensitive else logger.warning
                log_level(
                    f"Admin action completed - "
                    f"Action: {action_name}, "
                    f"User: {getattr(request.user, 'username', 'Anonymous')}, "
                    f"IP: {client_ip}, "
                    f"Status: {getattr(response, 'status_code', 'Unknown')}, "
                    f"Duration: {duration:.2f}s"
                )
                
                return response
                
            except Exception as e:
                # Log failed actions
                duration = (timezone.now() - start_time).total_seconds()
                logger.error(
                    f"Admin action failed - "
                    f"Action: {action_name}, "
                    f"User: {getattr(request.user, 'username', 'Anonymous')}, "
                    f"IP: {client_ip}, "
                    f"Error: {str(e)}, "
                    f"Duration: {duration:.2f}s"
                )
                raise e
                
        return _wrapped_view
    return decorator


def secure_admin_view(max_attempts=5, window_minutes=15, allowed_ips=None, 
                     audit_action=None, sensitive=False, methods=['GET', 'POST']):
    """
    Comprehensive security decorator combining all admin security features
    
    Args:
        max_attempts: Rate limit max attempts
        window_minutes: Rate limit window
        allowed_ips: IP whitelist
        audit_action: Action name for audit log
        sensitive: Whether this is a sensitive action
        methods: Allowed HTTP methods
    """
    def decorator(view_func):
        # Apply decorators in reverse order (they wrap around each other)
        secured_view = view_func
        
        # Audit logging (innermost)
        secured_view = audit_log_admin(action=audit_action, sensitive=sensitive)(secured_view)
        
        # Admin authentication required
        secured_view = admin_required(json_response=True)(secured_view)
        
        # IP whitelist
        if allowed_ips is not None:
            secured_view = ip_whitelist_required(allowed_ips)(secured_view)
        
        # Rate limiting
        secured_view = rate_limit_admin(max_attempts, window_minutes)(secured_view)
        
        # HTTP methods restriction
        secured_view = require_http_methods(methods)(secured_view)
        
        # CSRF protection
        secured_view = csrf_protect(secured_view)
        
        # Never cache admin responses
        secured_view = never_cache(secured_view)
        
        return secured_view
    return decorator


def session_timeout_required(timeout_minutes=30):
    """
    Decorator to check session timeout for admin users
    
    Args:
        timeout_minutes: Session timeout in minutes
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.is_superuser:
                last_activity = request.session.get('last_activity')
                
                if last_activity:
                    last_activity_time = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                    if timezone.is_naive(last_activity_time):
                        last_activity_time = timezone.make_aware(last_activity_time)
                    
                    # Check timeout
                    if timezone.now() - last_activity_time > timedelta(minutes=timeout_minutes):
                        logout(request)
                        client_ip = get_client_ip(request)
                        logger.info(f"Session timeout for admin user {request.user.username} from {client_ip}")
                        
                        if request.content_type == 'application/json' or 'api/' in request.path:
                            return JsonResponse({
                                'success': False,
                                'message': 'Session expired due to inactivity',
                                'redirect_url': '/admin-login/'
                            }, status=401)
                        else:
                            messages.warning(request, 'Your session has expired due to inactivity.')
                            return redirect('admin_login')
                
                # Update last activity
                request.session['last_activity'] = timezone.now().isoformat()
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# Utility functions

def get_client_ip(request):
    """Get the real client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'Unknown')
    return ip


def is_ip_allowed(client_ip, allowed_ips):
    """Check if IP is in the allowed list"""
    try:
        client_ip_obj = ip_address(client_ip)
        for allowed_ip in allowed_ips:
            try:
                if '/' in allowed_ip:
                    # CIDR notation
                    if client_ip_obj in ip_network(allowed_ip, strict=False):
                        return True
                else:
                    # Single IP
                    if client_ip_obj == ip_address(allowed_ip):
                        return True
            except ValueError:
                continue
        return False
    except ValueError:
        # Invalid IP format
        logger.error(f"Invalid IP format: {client_ip}")
        return False


# Predefined decorator combinations for common use cases

# For highly sensitive admin operations (user management, settings, etc.)
sensitive_admin_view = lambda func: secure_admin_view(
    max_attempts=3,
    window_minutes=10,
    audit_action=func.__name__,
    sensitive=True,
    methods=['GET', 'POST']
)(func)

# For regular admin operations (viewing data, basic operations)
standard_admin_view = lambda func: secure_admin_view(
    max_attempts=10,
    window_minutes=15,
    audit_action=func.__name__,
    sensitive=False
)(func)

# For admin API endpoints
admin_api_view = lambda func: secure_admin_view(
    max_attempts=20,
    window_minutes=10,
    audit_action=func.__name__,
    sensitive=False,
    methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
)(func)