from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from core.models import Category, Product, ProductImage
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test media upload functionality and Cloudinary configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-product',
            action='store_true',
            help='Create a test product with image to verify upload functionality',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up test products created by this command',
        )

    def handle(self, *args, **options):
        self.stdout.write("=== Media Upload Debug Test ===")
        
        # Test basic configuration
        self.test_configuration()
        
        # Test Cloudinary if enabled
        if getattr(settings, 'USE_CLOUDINARY_STORAGE', False):
            self.test_cloudinary_connection()
        
        if options['cleanup']:
            self.cleanup_test_data()
        elif options['create_test_product']:
            self.create_test_product()
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Use --create-test-product to test product creation or --cleanup to remove test data"
                )
            )

    def test_configuration(self):
        self.stdout.write("\n--- Configuration Test ---")
        
        # Check media settings
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"MEDIA_URL: {settings.MEDIA_URL}")
        self.stdout.write(f"MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'Not set')}")
        self.stdout.write(f"USE_CLOUDINARY_STORAGE: {getattr(settings, 'USE_CLOUDINARY_STORAGE', False)}")
        
        # Check Cloudinary settings
        cloudinary_url = getattr(settings, 'CLOUDINARY_URL', '')
        cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', '')
        api_key = getattr(settings, 'CLOUDINARY_API_KEY', '')
        api_secret = getattr(settings, 'CLOUDINARY_API_SECRET', '')
        
        if cloudinary_url:
            self.stdout.write(f"CLOUDINARY_URL: Set (length: {len(cloudinary_url)})")
        else:
            self.stdout.write("CLOUDINARY_URL: Not set")
            
        self.stdout.write(f"CLOUDINARY_CLOUD_NAME: {cloud_name or 'Not set'}")
        self.stdout.write(f"CLOUDINARY_API_KEY: {'Set' if api_key else 'Not set'}")
        self.stdout.write(f"CLOUDINARY_API_SECRET: {'Set' if api_secret else 'Not set'}")

    def test_cloudinary_connection(self):
        self.stdout.write("\n--- Cloudinary Connection Test ---")
        
        try:
            import cloudinary
            import cloudinary.api
            
            # Test API connection
            result = cloudinary.api.ping()
            if result.get('status') == 'ok':
                self.stdout.write(self.style.SUCCESS("✅ Cloudinary connection successful"))
                
                # Get account details
                try:
                    usage = cloudinary.api.usage()
                    self.stdout.write(f"Account plan: {usage.get('plan', 'Unknown')}")
                    self.stdout.write(f"Credits used: {usage.get('credits', 0)}")
                    self.stdout.write(f"Resources: {usage.get('resources', 0)}")
                except Exception as e:
                    self.stdout.write(f"Could not get usage info: {e}")
                    
            else:
                self.stdout.write(self.style.ERROR("❌ Cloudinary connection failed"))
                
        except ImportError:
            self.stdout.write(self.style.ERROR("❌ Cloudinary not installed"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Cloudinary connection error: {e}"))

    def create_test_image(self):
        """Create a simple test image"""
        # Create a simple colored image
        img = Image.new('RGB', (300, 300), color=(255, 100, 100))
        
        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=95)
        img_io.seek(0)
        
        return ContentFile(img_io.read(), name='test_image.jpg')

    def create_test_product(self):
        self.stdout.write("\n--- Creating Test Product ---")
        
        try:
            # Get or create test category
            category, created = Category.objects.get_or_create(
                slug='test-category',
                defaults={
                    'name': 'Test Category',
                    'description': 'Test category for debugging media uploads'
                }
            )
            
            if created:
                self.stdout.write("✅ Created test category")
            else:
                self.stdout.write("✅ Using existing test category")
                
            # Create test product
            product, created = Product.objects.get_or_create(
                slug='test-product-debug',
                defaults={
                    'name': 'Test Product (Debug)',
                    'description': 'This is a test product created for debugging media uploads. Safe to delete.',
                    'short_description': 'Test product for debugging',
                    'price': 100.00,
                    'category': category,
                    'sku': 'TEST-DEBUG-001',
                    'stock_quantity': 10,
                    'is_active': True,
                    'is_featured': False
                }
            )
            
            if created:
                self.stdout.write("✅ Created test product")
            else:
                self.stdout.write("✅ Using existing test product")
                # Clear existing images for fresh test
                product.images.all().delete()
                
            # Create test image
            self.stdout.write("Creating test image...")
            test_image = self.create_test_image()
            
            # Try to create ProductImage
            product_image = ProductImage(
                product=product,
                alt_text='Test image for debugging',
                is_primary=True,
                order=1
            )
            
            # Save the image
            product_image.image.save('test_debug_image.jpg', test_image, save=False)
            product_image.save()
            
            self.stdout.write(self.style.SUCCESS("✅ Test product and image created successfully!"))
            self.stdout.write(f"Product ID: {product.id}")
            self.stdout.write(f"Product URL: /products/{product.slug}/")
            
            if product_image.image:
                self.stdout.write(f"Image URL: {product_image.image.url}")
                self.stdout.write(f"Storage class: {product_image.image.storage.__class__.__name__}")
                
            if product_image.optimized_image:
                self.stdout.write(f"Optimized image URL: {product_image.optimized_image.url}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating test product: {e}"))
            logger.exception("Error in create_test_product")
            
            # Additional debugging
            import traceback
            self.stdout.write("\nFull error traceback:")
            self.stdout.write(traceback.format_exc())

    def cleanup_test_data(self):
        self.stdout.write("\n--- Cleaning Up Test Data ---")
        
        try:
            # Delete test products
            test_products = Product.objects.filter(slug__startswith='test-product-debug')
            count = test_products.count()
            if count > 0:
                test_products.delete()
                self.stdout.write(f"✅ Deleted {count} test product(s)")
            else:
                self.stdout.write("No test products found to delete")
                
            # Delete test categories if they have no products
            test_categories = Category.objects.filter(slug='test-category')
            for category in test_categories:
                if category.products.count() == 0:
                    category.delete()
                    self.stdout.write("✅ Deleted empty test category")
                else:
                    self.stdout.write("Kept test category (has other products)")
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during cleanup: {e}"))