from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        user = User.objects.create(email='admin@admin.com')
        user.set_password('123zxc')
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
