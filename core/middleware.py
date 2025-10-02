from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
import logging
import json
from datetime import datetime, timedelta
from ipaddress import ip_address, ip_network
import re

logger = logging.getLogger('security')


class AdminSecurityMiddleware(MiddlewareMixin):
    """
    Comprehensive security middleware for admin access protection
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_paths = [
            '/admin-login/',
            '/admin-dashboard/',
            '/admin/',
            '/api/auth/login/',
            '/admin/login/',
        ]
        super().__init__(get_response)

    def process_request(self, request):
        """Process incoming request for security checks"""
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        request.client_ip = client_ip
        
        # Check if accessing admin areas
        if self.is_admin_path(request.path):
            # Rate limiting for admin login attempts
            if self.is_login_path(request.path) and request.method == 'POST':
                if self.is_rate_limited(client_ip):
                    logger.warning(f"Rate limit exceeded for IP {client_ip} on admin login")
                    return self.rate_limit_response(request)
                
                # Track login attempt
                self.track_login_attempt(client_ip, request)
            
            # Check IP whitelist (if configured)
            if not self.is_ip_allowed(client_ip):
                logger.warning(f"Blocked admin access from unauthorized IP: {client_ip}")
                return HttpResponseForbidden("Access denied from your IP address")
            
            # Admin dashboard protection
            if self.is_admin_dashboard(request.path):
                if not self.is_admin_authenticated(request):
                    logger.info(f"Redirecting unauthenticated user from {client_ip} to login")
                    return redirect('admin_login')
                
                # Check session validity
                if not self.is_session_valid(request):
                    logout(request)
                    messages.error(request, "Session expired. Please login again.")
                    logger.info(f"Session expired for user from {client_ip}")
                    return redirect('admin_login')
        
        return None

    def process_response(self, request, response):
        """Process response to add security headers"""
        
        # Add security headers for admin pages
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superuser:
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # Log admin login attempts
        if (hasattr(request, 'client_ip') and 
            self.is_login_path(request.path) and 
            request.method == 'POST'):
            self.log_login_attempt(request, response)
        
        return response

    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        return ip

    def is_admin_path(self, path):
        """Check if the path is an admin-related path"""
        return any(path.startswith(admin_path) for admin_path in self.admin_paths)

    def is_login_path(self, path):
        """Check if the path is a login endpoint"""
        login_paths = ['/admin-login/', '/admin/login/', '/api/auth/login/']
        return any(path.startswith(login_path) for login_path in login_paths)

    def is_admin_dashboard(self, path):
        """Check if the path is admin dashboard"""
        return path.startswith('/admin-dashboard/') or path.startswith('/admin/')

    def is_admin_authenticated(self, request):
        """Check if user is authenticated and is admin"""
        return (request.user.is_authenticated and 
                request.user.is_superuser and 
                request.user.is_active)

    def is_session_valid(self, request):
        """Check if the current session is valid"""
        if not request.user.is_authenticated:
            return False
        
        # Check session age (4 hours max)
        session_start = request.session.get('admin_session_start')
        if not session_start:
            # Set session start time if not exists
            request.session['admin_session_start'] = timezone.now().isoformat()
            return True
        
        session_start_time = datetime.fromisoformat(session_start.replace('Z', '+00:00'))
        if timezone.is_naive(session_start_time):
            session_start_time = timezone.make_aware(session_start_time)
        
        session_age = timezone.now() - session_start_time
        max_age = timedelta(hours=4)  # 4 hour session timeout
        
        return session_age < max_age

    def is_rate_limited(self, ip):
        """Check if IP is rate limited for login attempts"""
        cache_key = f"admin_login_attempts:{ip}"
        attempts = cache.get(cache_key, 0)
        
        # Allow 5 attempts per 15 minutes
        max_attempts = 5
        return attempts >= max_attempts

    def is_ip_allowed(self, ip):
        """Check if IP is in whitelist (if configured)"""
        # Get IP whitelist from settings
        allowed_ips = getattr(settings, 'ADMIN_ALLOWED_IPS', [])
        
        if not allowed_ips:
            return True  # No whitelist configured, allow all
        
        try:
            client_ip = ip_address(ip)
            for allowed_ip in allowed_ips:
                try:
                    if '/' in allowed_ip:
                        # CIDR notation
                        if client_ip in ip_network(allowed_ip, strict=False):
                            return True
                    else:
                        # Single IP
                        if client_ip == ip_address(allowed_ip):
                            return True
                except ValueError:
                    continue
            return False
        except ValueError:
            # Invalid IP format
            logger.error(f"Invalid IP format: {ip}")
            return False

    def track_login_attempt(self, ip, request):
        """Track login attempts for rate limiting"""
        cache_key = f"admin_login_attempts:{ip}"
        attempts = cache.get(cache_key, 0)
        cache.set(cache_key, attempts + 1, timeout=900)  # 15 minutes

    def rate_limit_response(self, request):
        """Return rate limit exceeded response"""
        if request.content_type == 'application/json' or 'api/' in request.path:
            return JsonResponse({
                'success': False,
                'message': 'Too many login attempts. Please try again in 15 minutes.',
                'retry_after': 900
            }, status=429)
        else:
            return HttpResponse(
                "Too many login attempts. Please try again in 15 minutes.",
                status=429
            )

    def log_login_attempt(self, request, response):
        """Log admin login attempts"""
        client_ip = getattr(request, 'client_ip', 'Unknown')
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Determine if login was successful
        success = False
        username = 'Unknown'
        
        try:
            if hasattr(response, 'content'):
                if response.status_code == 200:
                    if request.content_type == 'application/json':
                        try:
                            content = json.loads(response.content)
                            success = content.get('success', False)
                        except (json.JSONDecodeError, AttributeError):
                            pass
                    else:
                        # For non-JSON responses, assume success if user is authenticated after login
                        success = (hasattr(request, 'user') and 
                                 request.user.is_authenticated and 
                                 request.user.is_superuser)
            
            # Try to get username from request
            if request.content_type == 'application/json':
                try:
                    body = json.loads(request.body.decode('utf-8'))
                    username = body.get('username', 'Unknown')
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
            else:
                username = request.POST.get('username', 'Unknown')
                
        except Exception as e:
            logger.error(f"Error parsing login attempt: {e}")

        # Log the attempt
        log_message = (
            f"Admin login attempt - "
            f"IP: {client_ip}, "
            f"Username: {username}, "
            f"Success: {success}, "
            f"User-Agent: {user_agent[:100]}..."  # Truncate long user agents
        )
        
        if success:
            logger.info(log_message)
        else:
            logger.warning(log_message)
            
            # Track failed attempts for additional security
            self.track_failed_attempt(client_ip, username)

    def track_failed_attempt(self, ip, username):
        """Track failed login attempts for security monitoring"""
        timestamp = timezone.now().isoformat()
        
        # Store in cache for recent monitoring
        failed_key = f"failed_admin_logins:{ip}"
        failed_attempts = cache.get(failed_key, [])
        failed_attempts.append({
            'username': username,
            'timestamp': timestamp
        })
        
        # Keep only last 10 attempts
        failed_attempts = failed_attempts[-10:]
        cache.set(failed_key, failed_attempts, timeout=3600)  # 1 hour
        
        # Log critical security events
        if len(failed_attempts) >= 3:
            logger.critical(
                f"Multiple failed admin login attempts from {ip} - "
                f"Usernames: {[attempt['username'] for attempt in failed_attempts[-3:]]}"
            )


class AdminSessionTimeoutMiddleware(MiddlewareMixin):
    """
    Middleware to handle admin session timeouts
    """
    
    def process_request(self, request):
        """Check and handle session timeouts for admin users"""
        if (request.user.is_authenticated and 
            request.user.is_superuser and 
            request.path.startswith('/admin')):
            
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity_time = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                if timezone.is_naive(last_activity_time):
                    last_activity_time = timezone.make_aware(last_activity_time)
                
                # Check if session has been inactive for more than 30 minutes
                if timezone.now() - last_activity_time > timedelta(minutes=30):
                    logout(request)
                    messages.warning(request, "Your session has expired due to inactivity.")
                    logger.info(f"Admin session expired for user {request.user.username}")
                    return redirect('admin_login')
            
            # Update last activity
            request.session['last_activity'] = timezone.now().isoformat()
        
        return None