# myapp/management/commands/my_command.py
from django.core.management.base import BaseCommand
from apps__campaigns.create_campaign_template import run

class Command(BaseCommand):
    help = 'Description of your command'

    def handle(self, *args, **options):
        run()