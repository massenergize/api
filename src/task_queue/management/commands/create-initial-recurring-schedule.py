from django.core.management.base import BaseCommand

from task_queue.database_tasks.create_initial_schedule_for_recurring_events import create_initial_schedule


class Command(BaseCommand):
    help = 'Back fill menu for all communities'

    def handle(self, *args, **options):
        create_initial_schedule()