from django.apps import AppConfig


class PlantationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plantation'

    def ready(self):
        from . import signals
        print("\n✓ TreeForLife Signals Initialized:")
        print("  ├── VisitRequest status change")
        print("  ├── Timeline creation")
        print("  ├── Comment notifications")
        print("  ├── User creation")
        print("  ├── Plantation assignment")
        print("  ├── Employee creation")
        print("  └── Corporate notifications")
