from django.apps import AppConfig

class MiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MiApp'

    def ready(self):
        import MiApp.signals  # Importa las señales aquí
