from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, Product, AdminUser
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Populate initial data for Jossie SmartHome'

    def handle(self, *args, **options):
        self.stdout.write('Creating initial data...')
        
        # Create categories
        categories_data = [
            {
                'name': 'Kitchen',
                'description': 'Essential kitchen tools and accessories for cooking and food preparation',
            },
            {
                'name': 'Dining',
                'description': 'Elegant dining accessories, tableware, and serving pieces',
            },
            {
                'name': 'Bedding',
                'description': 'Comfortable and stylish bedding sets, pillows, and bedroom accessories',
            },
            {
                'name': 'Storage',
                'description': 'Smart storage solutions and organizational products for every room',
            },
            {
                'name': 'Bathroom',
                'description': 'Luxurious bathroom accessories and essentials for daily comfort',
            },
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        # Create sample products
        kitchen_category = Category.objects.get(name='Kitchen')
        dining_category = Category.objects.get(name='Dining')
        bedding_category = Category.objects.get(name='Bedding')
        storage_category = Category.objects.get(name='Storage')
        bathroom_category = Category.objects.get(name='Bathroom')
        
        products_data = [
            # Kitchen Products
            {
                'name': 'Premium Chef Knife Set',
                'category': kitchen_category,
                'description': 'Professional-grade stainless steel knife set with ergonomic handles. Perfect for all your culinary needs.',
                'short_description': 'Professional stainless steel knife set',
                'price': 8999.00,
                'original_price': 12999.00,
                'sku': 'KIT-KNIFE-001',
                'stock_quantity': 25,
                'weight': 2.5,  # kg
                'dimensions': '35cm x 25cm x 5cm',
                'is_featured': True,
            },
            {
                'name': 'Non-Stick Cookware Set',
                'category': kitchen_category,
                'description': 'Complete 12-piece non-stick cookware set with heat-resistant handles and even heat distribution.',
                'short_description': '12-piece non-stick cookware collection',
                'price': 14999.00,
                'original_price': 18999.00,
                'sku': 'KIT-COOK-002',
                'stock_quantity': 15,
                'weight': 8.2,
                'dimensions': '45cm x 35cm x 20cm',
                'is_featured': True,
            },
            {
                'name': 'Bamboo Cutting Board Set',
                'category': kitchen_category,
                'description': 'Eco-friendly bamboo cutting boards in three sizes with built-in compartments for easy food prep.',
                'short_description': 'Eco-friendly bamboo cutting board set',
                'price': 3499.00,
                'original_price': 4499.00,
                'sku': 'KIT-BOARD-003',
                'stock_quantity': 40,
                'weight': 1.8,
                'dimensions': '40cm x 30cm x 3cm',
            },
            
            # Dining Products
            {
                'name': 'Elegant Dinnerware Set',
                'category': dining_category,
                'description': '16-piece porcelain dinnerware set with modern design, perfect for everyday dining and special occasions.',
                'short_description': '16-piece porcelain dinnerware set',
                'price': 7999.00,
                'original_price': 9999.00,
                'sku': 'DIN-PLATE-001',
                'stock_quantity': 20,
                'weight': 4.5,
                'dimensions': '30cm x 30cm x 25cm',
                'is_featured': True,
            },
            {
                'name': 'Crystal Wine Glass Set',
                'category': dining_category,
                'description': 'Set of 6 handcrafted crystal wine glasses with elegant stems, perfect for wine enthusiasts.',
                'short_description': 'Handcrafted crystal wine glasses',
                'price': 5999.00,
                'original_price': 7499.00,
                'sku': 'DIN-GLASS-002',
                'stock_quantity': 30,
                'weight': 1.2,
                'dimensions': '25cm x 20cm x 15cm',
            },
            
            # Bedding Products
            {
                'name': 'Luxury Egyptian Cotton Sheets',
                'category': bedding_category,
                'description': '1000 thread count Egyptian cotton sheet set with deep pockets and silky smooth finish.',
                'short_description': '1000TC Egyptian cotton sheet set',
                'price': 11999.00,
                'original_price': 15999.00,
                'sku': 'BED-SHEET-001',
                'stock_quantity': 35,
                'weight': 2.0,
                'dimensions': '180cm x 200cm x 30cm',
                'is_featured': True,
            },
            {
                'name': 'Memory Foam Pillow Set',
                'category': bedding_category,
                'description': 'Set of 2 contoured memory foam pillows with cooling gel technology for optimal sleep comfort.',
                'short_description': 'Memory foam pillows with cooling gel',
                'price': 6999.00,
                'original_price': 8499.00,
                'sku': 'BED-PILLOW-002',
                'stock_quantity': 50,
                'weight': 3.2,
                'dimensions': '50cm x 30cm x 15cm',
            },
            
            # Storage Products
            {
                'name': 'Modular Storage Bins',
                'category': storage_category,
                'description': 'Set of 6 stackable storage bins with clear fronts and labels for organized home storage.',
                'short_description': 'Stackable storage bins with labels',
                'price': 3999.00,
                'original_price': 4999.00,
                'sku': 'STO-BIN-001',
                'stock_quantity': 45,
                'weight': 4.8,
                'dimensions': '40cm x 30cm x 25cm',
            },
            {
                'name': 'Under-Bed Storage Box',
                'category': storage_category,
                'description': 'Large under-bed storage container with wheels and zippered top, perfect for seasonal items.',
                'short_description': 'Wheeled under-bed storage container',
                'price': 2499.00,
                'original_price': 3299.00,
                'sku': 'STO-UNDER-002',
                'stock_quantity': 60,
                'weight': 2.1,
                'dimensions': '90cm x 45cm x 15cm',
            },
            
            # Bathroom Products
            {
                'name': 'Luxury Towel Set',
                'category': bathroom_category,
                'description': '6-piece Turkish cotton towel set with exceptional absorbency and softness.',
                'short_description': 'Turkish cotton luxury towel set',
                'price': 8999.00,
                'original_price': 11999.00,
                'sku': 'BAT-TOWEL-001',
                'stock_quantity': 25,
                'weight': 3.5,
                'dimensions': '70cm x 140cm x 10cm',
                'is_featured': True,
            },
            {
                'name': 'Bamboo Bathroom Organizer',
                'category': bathroom_category,
                'description': 'Multi-tier bamboo organizer with drawers and compartments for bathroom essentials.',
                'short_description': 'Multi-tier bamboo bathroom organizer',
                'price': 4999.00,
                'original_price': 6499.00,
                'sku': 'BAT-ORG-002',
                'stock_quantity': 18,
                'weight': 5.2,
                'dimensions': '35cm x 25cm x 80cm',
            },
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults={
                    'name': product_data['name'],
                    'slug': slugify(product_data['name']),
                    'category': product_data['category'],
                    'description': product_data['description'],
                    'short_description': product_data['short_description'],
                    'price': product_data['price'],
                    'original_price': product_data.get('original_price'),
                    'stock_quantity': product_data['stock_quantity'],
                    'is_active': True,
                    'is_featured': product_data.get('is_featured', False),
                    'low_stock_threshold': 10,
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'Product already exists: {product.name}')
        
        # Create admin user profile if admin user exists
        try:
            admin_user = User.objects.get(username='admin')
            admin_profile, created = AdminUser.objects.get_or_create(
                user=admin_user,
                defaults={
                    'phone': '+1234567890',
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write('Created admin user profile')
            else:
                self.stdout.write('Admin user profile already exists')
        except User.DoesNotExist:
            self.stdout.write('Admin user not found. Please create superuser first.')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated initial data!'))