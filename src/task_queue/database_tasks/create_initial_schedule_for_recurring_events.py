from _main_.utils.massenergize_logger import log
from api.tasks import update_recurring_event
from database.models import Event


def create_initial_schedule():
    events = Event.objects.filter(is_recurring=True, is_deleted=False, recurring_details__isnull=False)
    
    for event in events:
        log.info(f"==== Initial Schedule for: {event.name}======")
        update_recurring_event(str(event.id))
        log.info(f"==== DONE: for {event.name}====")