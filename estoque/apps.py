from django.apps import AppConfig

class EstoqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'estoque'

    def ready(self):
        # Try to create groups if possible (safe to fail during migrations)
        try:
            from django.contrib.auth.models import Group
            Group.objects.get_or_create(name='Gestor')
            Group.objects.get_or_create(name='Colaborador')
        except Exception:
            pass
