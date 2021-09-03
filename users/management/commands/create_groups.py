from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create group admin'

    def handle(self, *args, **kwargs):
        Group.objects.create(name='admin')