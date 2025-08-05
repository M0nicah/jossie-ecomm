from django.core.management.base import BaseCommand
from core.models import Product, ProductImage
from django.core.files.base import ContentFile
from PIL import Image
import os


class Command(BaseCommand):
    help = 'Add sample images to existing products'

    def handle(self, *args, **options):
        self.stdout.write('Adding sample images to products...')
        
        # Create simple colored placeholder images
        self.create_placeholder_images()
        
        products = Product.objects.all()
        for product in products:
            if not product.images.exists():
                self.add_sample_image_to_product(product)
                self.stdout.write(f'Added sample image to: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully added sample images!'))
    
    def create_placeholder_images(self):
        """Create simple colored placeholder images"""
        colors = [
            (255, 107, 53),   # Orange (primary)
            (5, 150, 105),    # Green (success)
            (59, 130, 246),   # Blue
            (168, 85, 247),   # Purple
            (236, 72, 153),   # Pink
        ]
        
        os.makedirs('media/products', exist_ok=True)
        
        for i, color in enumerate(colors):
            # Create a simple colored square image
            img = Image.new('RGB', (400, 400), color)
            img_path = f'media/products/sample_{i+1}.jpg'
            
            if not os.path.exists(img_path):
                img.save(img_path, 'JPEG', quality=85)
                self.stdout.write(f'Created sample image: sample_{i+1}.jpg')
    
    def add_sample_image_to_product(self, product):
        """Add a sample image to a product"""
        import random
        
        # Choose a random sample image
        sample_num = random.randint(1, 5)
        image_path = f'products/sample_{sample_num}.jpg'
        
        # Create ProductImage
        product_image = ProductImage.objects.create(
            product=product,
            image=image_path,
            alt_text=f'{product.name} image',
            is_primary=True,
            order=0
        )
        
        return product_image