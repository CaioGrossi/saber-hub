from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_certificate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='content_type',
        ),
    ]
