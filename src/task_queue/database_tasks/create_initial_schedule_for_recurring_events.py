from database.models import Event
from task_queue.database_tasks.update_recurring_events import update_recurring_event


def create_initial_schedule():
    events = Event.objects.filter(is_recurring=True, is_deleted=False, recurring_details__isnull=False)
    for event in events:
        update_recurring_event(event.id)
    return True
        
