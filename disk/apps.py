from django.apps import AppConfig


class PanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'disk'
    verbose_name = 'network disk'

    def ready(self):
        import disk.signals
