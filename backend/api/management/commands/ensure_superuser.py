import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates or updates the superuser from environment variables'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" created successfully.')
            )
            return

        # User exists — ensure they are a superuser and sync the password.
        changed = False

        if not user.is_superuser or not user.is_staff:
            user.is_superuser = True
            user.is_staff = True
            changed = True

        if email and user.email != email:
            user.email = email
            changed = True

        user.set_password(password)
        changed = True

        if changed:
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" updated successfully.')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Superuser "{username}" already up to date.')
            )
