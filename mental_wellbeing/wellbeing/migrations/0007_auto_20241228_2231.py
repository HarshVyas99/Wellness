# Generated by Django 3.2.25 on 2024-12-28 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wellbeing', '0006_meditationcontent'),
    ]

    operations = [
        migrations.CreateModel(
            name='MentalWellbeingContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content_type', models.CharField(choices=[('article', 'Article'), ('self_care_tip', 'Self-care Tip'), ('practice', 'Practice'), ('resource', 'Resource'), ('video', 'Video')], max_length=20)),
                ('url', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('video_file', models.FileField(blank=True, null=True, upload_to='meditation_videos/')),
                ('image', models.ImageField(blank=True, null=True, upload_to='meditation_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='MeditationContent',
        ),
    ]
