from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json


@csrf_exempt
@require_http_methods(["POST"])
def admin_login_view(request):
    """Admin login view"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Username and password are required'
            }, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'redirect_url': '/admin-dashboard/'
            })
        else:
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


@require_http_methods(["POST", "GET"])
def admin_logout_view(request):
    """Admin logout view"""
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