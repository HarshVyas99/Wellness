# Generated by Django 3.2.25 on 2024-12-28 12:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wellbeing', '0002_auto_20241228_1647'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('bio', models.TextField(blank=True, null=True)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('interests', models.CharField(blank=True, choices=[('sports', 'Sports'), ('music', 'Music'), ('movies', 'Movies'), ('technology', 'Technology'), ('reading', 'Reading'), ('traveling', 'Traveling'), ('art', 'Art'), ('gaming', 'Gaming')], max_length=100, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]