from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default admin user if it does not exist"

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(username="admin").exists():
            self.stdout.write("Admin user already exists — skipping.")
            return
        User.objects.create_superuser(
            username="admin",
            email="admin@rsm.id",
            password="admin123",
        )
        self.stdout.write(self.style.SUCCESS(
            "Default admin created: username=admin password=admin123"
            " — CHANGE THIS PASSWORD in production!"
        ))
