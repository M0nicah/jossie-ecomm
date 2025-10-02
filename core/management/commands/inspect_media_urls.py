from django.core.management.base import BaseCommand

from core.models import Category, ProductImage


class Command(BaseCommand):
    help = "Inspect a few media file URLs to verify storage configuration"

    def handle(self, *args, **options):
        categories = Category.objects.exclude(image='')[:5]
        if not categories:
            self.stdout.write('No category images found to inspect.')
        else:
            self.stdout.write('Category image URLs:')
            for category in categories:
                url = category.image.url if category.image else '[no image uploaded]'
                storage = category.image.storage.__class__.__name__ if category.image else 'N/A'
                self.stdout.write(f" - {category.name}: {url} ({storage})")

        images = ProductImage.objects.exclude(image='')[:10]
        if not images:
            self.stdout.write('No product images found to inspect.')
        else:
            self.stdout.write('Product image URLs:')
            for img in images:
                url = img.image.url if img.image else '[no image uploaded]'
                storage = img.image.storage.__class__.__name__ if img.image else 'N/A'
                self.stdout.write(
                    f" - Product {img.product_id} image {img.pk}: {url} ({storage})"
                )
