"""
Service layer for business logic
"""
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import transaction, close_old_connections
import urllib.parse
from typing import Dict, Any


class WhatsAppService:
    """Service for WhatsApp integration"""
    
    @staticmethod
    def generate_order_message(order) -> str:
        """Generate WhatsApp message for order"""
        message = f"""🛍️ New Order - {settings.WHATSAPP_BUSINESS_NAME}

📋 Order Details:
• Order ID: {order.order_id}
• Customer: {order.first_name} {order.last_name}
• Email: {order.email}
• Phone: {order.phone}

📦 Items Ordered:"""
        
        for item in order.items.all():
            message += f"\n• {item.product_name} x{item.quantity} - KES {int(item.product_price):,}"
        
        message += f"""

💰 Subtotal: KES {int(order.subtotal_amount):,}
🚚 Shipping: KES {int(order.shipping_fee):,}
💰 Total Amount: KES {int(order.total_amount):,}

📍 Delivery Instructions:
{order.delivery_notes}"""

        if order.notes:
            message += f"\n\n📝 Special Instructions:\n{order.notes}"
        
        message += f"""

✅ Please confirm this order to proceed with payment and delivery.

Thank you for choosing {settings.WHATSAPP_BUSINESS_NAME}! 🙏"""
        
        return message
    
    @staticmethod
    def generate_whatsapp_url(order) -> str:
        """Generate WhatsApp URL for order"""
        message = WhatsAppService.generate_order_message(order)
        encoded_message = urllib.parse.quote(message)
        phone_number = settings.WHATSAPP_BUSINESS_NUMBER.replace('+', '').replace(' ', '').replace('-', '')
        
        return f"https://wa.me/{phone_number}?text={encoded_message}"
    
    @staticmethod
    def generate_admin_notification_message(order) -> str:
        """Generate admin notification message"""
        message = f"""🔔 New Order Alert!

Order #{str(order.order_id).split('-')[0]}
Customer: {order.first_name} {order.last_name}
Total: KES {int(order.total_amount):,}
Items: {order.total_items}

Check your admin dashboard for full details."""
        
        return message
    
    @staticmethod
    def generate_admin_whatsapp_url(order) -> str:
        """Generate WhatsApp URL for admin notification"""
        message = WhatsAppService.generate_admin_notification_message(order)
        encoded_message = urllib.parse.quote(message)
        phone_number = settings.WHATSAPP_BUSINESS_NUMBER.replace('+', '').replace(' ', '').replace('-', '')
        
        # This would typically go to admin's personal WhatsApp
        return f"https://wa.me/{phone_number}?text={encoded_message}"


class EmailService:
    """Service for email notifications"""
    
    @staticmethod
    def send_order_confirmation(order):
        """Send order confirmation email to customer"""
        try:
            subject = f"Order Confirmation - {order.order_id}"
            
            # Render email template
            html_message = render_to_string('emails/order_confirmation.html', {
                'order': order,
                'business_name': settings.WHATSAPP_BUSINESS_NAME,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return True
        except Exception as e:
            print(f"Error sending order confirmation email: {e}")
            return False
    
    @staticmethod
    def send_admin_notification(order):
        """Send new order notification to admin"""
        try:
            subject = f"New Order Alert - #{order.order_id}"
            
            # Render admin email template
            html_message = render_to_string('emails/admin_order_notification.html', {
                'order': order,
                'business_name': settings.WHATSAPP_BUSINESS_NAME,
            })
            plain_message = strip_tags(html_message)
            
            # Send to admin email (you would configure this)
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@jossiefancies.com')
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return True
        except Exception as e:
            print(f"Error sending admin notification email: {e}")
            return False


class OrderService:
    """Service for order processing"""
    
    @staticmethod
    def process_new_order(order):
        """Process a newly created order"""
        try:
            transaction.on_commit(lambda: _send_order_notifications(order.id))
            return True
        except Exception as e:
            print(f"Error processing new order: {e}")
            return False
    
    @staticmethod
    def get_order_analytics():
        """Get order analytics for dashboard"""
        from .models import Order
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta
        
        # Get date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        analytics = {
            'total_orders': Order.objects.count(),
            'total_revenue': Order.objects.aggregate(
                total=Sum('total_amount')
            )['total'] or 0,
            'orders_today': Order.objects.filter(created_at__date=today).count(),
            'orders_this_week': Order.objects.filter(created_at__date__gte=week_ago).count(),
            'orders_this_month': Order.objects.filter(created_at__date__gte=month_ago).count(),
            'revenue_this_month': Order.objects.filter(
                created_at__date__gte=month_ago
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            'pending_orders': Order.objects.filter(status='pending').count(),
            'confirmed_orders': Order.objects.filter(status='confirmed').count(),
            'status_breakdown': Order.objects.values('status').annotate(
                count=Count('id')
            ).order_by('status'),
        }
        
        return analytics


class InventoryService:
    """Service for inventory management"""
    
    @staticmethod
    def get_low_stock_products():
        """Get products with low stock"""
        from .models import Product
        from django.db import models
        
        return Product.objects.filter(
            stock_quantity__lte=models.F('low_stock_threshold'),
            is_active=True
        ).select_related('category')
    
    @staticmethod
    def update_stock_after_order(order):
        """Update stock quantities after an order"""
        from .models import StockHistory
        
        for item in order.items.all():
            product = item.product
            previous_stock = product.stock_quantity
            
            # Update stock
            product.stock_quantity -= item.quantity
            product.save(update_fields=['stock_quantity'])
            
            # Create stock history record
            StockHistory.objects.create(
                product=product,
                transaction_type='sale',
                quantity_change=-item.quantity,
                previous_stock=previous_stock,
                new_stock=product.stock_quantity,
                reason=f'Order {order.order_id}',
                order=order
            )
    
    @staticmethod
    def get_inventory_alerts():
        """Get inventory alerts for dashboard"""
        from .models import Product
        from django.db import models
        
        low_stock = Product.objects.filter(
            stock_quantity__lte=models.F('low_stock_threshold'),
            is_active=True
        ).count()
        
        out_of_stock = Product.objects.filter(
            stock_quantity=0,
            is_active=True
        ).count()
        
        return {
            'low_stock_count': low_stock,
            'out_of_stock_count': out_of_stock,
            'total_alerts': low_stock + out_of_stock
        }


def _send_order_notifications(order_id: int) -> None:
    """Background worker for sending order notifications."""
    from .models import Order  # Local import to avoid circular dependency

    close_old_connections()

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    customer_sent = EmailService.send_order_confirmation(order)
    admin_sent = EmailService.send_admin_notification(order)

    if customer_sent and admin_sent and not order.whatsapp_sent:
        order.whatsapp_sent = True
        order.save(update_fields=['whatsapp_sent'])
