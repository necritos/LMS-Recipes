from django.core.management.base import BaseCommand

from apps.catalog.models import Language


class Command(BaseCommand):
    help = "Carga idiomas iniciales (ES, EN)."

    def handle(self, *args, **options):
        defaults = [
            ("es", "Español"),
            ("en", "English"),
        ]
        for code, name in defaults:
            language, created = Language.objects.get_or_create(
                code=code,
                defaults={"name": name, "is_active": True},
            )
            action = "creado" if created else "ya existía"
            self.stdout.write(f"  {code}: {action}")
