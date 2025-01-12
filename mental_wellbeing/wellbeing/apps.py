from django.apps import AppConfig


class WellbeingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wellbeing'

    def ready(self):
        import wellbeing.signals  # Ensure signals are loaded