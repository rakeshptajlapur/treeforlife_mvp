from django.apps import AppConfig


class PlantationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plantation'

    def ready(self):
        import plantation.signals
