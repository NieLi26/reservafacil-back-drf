from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create Super user'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'adminadmin'
        email = 'admin@example.com'

        if not CustomUser.objects.filter(username=username).exists():
            CustomUser.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists.'))
