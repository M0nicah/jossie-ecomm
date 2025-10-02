from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Report whether Cloudinary storage is active and which credentials are loaded"

    def handle(self, *args, **options):
        use_cloudinary = getattr(settings, 'USE_CLOUDINARY_STORAGE', False)

        if not use_cloudinary:
            self.stdout.write(self.style.WARNING(
                'Cloudinary storage disabled. MEDIA_URL=%s MEDIA_ROOT=%s'
                % (getattr(settings, 'MEDIA_URL', ''), getattr(settings, 'MEDIA_ROOT', ''))
            ))
            missing = []
            if not getattr(settings, 'CLOUDINARY_URL', ''):
                missing.append('CLOUDINARY_URL')
            if not getattr(settings, 'CLOUDINARY_CLOUD_NAME', ''):
                missing.append('CLOUDINARY_CLOUD_NAME')
            if not getattr(settings, 'CLOUDINARY_API_KEY', ''):
                missing.append('CLOUDINARY_API_KEY')
            if not getattr(settings, 'CLOUDINARY_API_SECRET', ''):
                missing.append('CLOUDINARY_API_SECRET')
            if missing:
                self.stdout.write(self.style.WARNING(
                    'Missing or empty env vars: %s' % ', '.join(missing)
                ))
            return

        self.stdout.write(self.style.SUCCESS('Cloudinary storage enabled.'))

        try:
            import cloudinary
        except ImportError:  # pragma: no cover - such failure would break elsewhere too
            self.stdout.write(self.style.ERROR('cloudinary package not installed.'))
            return

        cloudinary_config = cloudinary.config()
        self.stdout.write('Cloud name: %s' % (cloudinary_config.cloud_name or '[unset]'))
        self.stdout.write('Secure: %s' % ('yes' if getattr(cloudinary_config, 'secure', False) else 'no'))

        storage = getattr(settings, 'CLOUDINARY_STORAGE', {})
        if storage:
            self.stdout.write('CLOUDINARY_STORAGE configured.')
        else:
            self.stdout.write(self.style.WARNING('CLOUDINARY_STORAGE dict not set.'))
