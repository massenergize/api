from django.core.management.base import BaseCommand
from task_queue.database_tasks.menu_backfill import back_fill_menu


class Command(BaseCommand):
    help = 'Back fill menu for all communities'

    def handle(self, *args, **options):
        back_fill_menu()