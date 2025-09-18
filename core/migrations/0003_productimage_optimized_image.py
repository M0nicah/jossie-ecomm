from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_order_address_remove_order_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='optimized_image',
            field=models.ImageField(blank=True, editable=False, null=True, upload_to='products/optimized/'),
        ),
    ]
