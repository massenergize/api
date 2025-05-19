from task_queue.database_tasks.contents_spacing_correction import process_spacing_data
from task_queue.database_tasks.media_library_cleanup import remove_duplicate_images
from task_queue.database_tasks.shedule_admin_messages import schedule_admin_messages
from task_queue.database_tasks.translate_db_content import TranslateDBContents
from task_queue.database_tasks.update_actions_content import update_actions_content
from task_queue.nudges.cadmin_events_nudge import send_events_nudge
from task_queue.nudges.cadmin_testimonial_nudge import prepare_testimonials_for_community_admins
from task_queue.nudges.postmark_nudge_report import generate_postmark_nudge_report
from task_queue.nudges.user_event_nudge import prepare_user_events_nudge
from task_queue.nudges.postmark_sender_signature import collect_and_create_signatures
from task_queue.views import super_admin_nudge, create_snapshots, send_admin_mou_notification
from .constants import (
  SEND_SCHEDULED_EMAIL, TEST, SUPER_ADMIN_NUDGE, COMMUNITY_ADMIN_NUDGE, ADMIN_MOU_NOTIFIER,
    USER_EVENT_NUDGE, CREATE_COMMUNITY_SNAPSHOTS, POSTMARK_SENDER_SIGNATURE,
    PROCESS_CONTENT_SPACING, UPDATE_ACTION_CONTENT, REMOVE_DUPLICATE_IMAGES,
    TRANSLATE_DB_CONTENTS, COMMUNITY_ADMIN_TESTIMONIAL_NUDGE, POSTMARK_NUDGE_REPORT
)

"""
Task Queue System Documentation:

1. Task Function Requirements:
   - All functions must accept a task parameter
   - Functions must be wrapped in try-except blocks
   - Functions must return a tuple of (success: bool, error: Optional[Exception])

2. Dictionary Management:
   - Do not modify existing dictionary keys
   - Do not remove tasks that are in use
   - Only add new items to the dictionaries

3. Scheduled Messages:
   - Created with one_off=True and is_automatic_task=True
   - Scheduled time is set to the message's scheduled time
"""

def test(task):
    """Test function for task queue system."""
    return True, None

# Hidden tasks that are not exposed in the main interface
AUTOMATIC_TASK_FUNCTIONS = {
    SEND_SCHEDULED_EMAIL: schedule_admin_messages,
}

# Main task function registry
FUNCTIONS = {
    TEST: test,
    SUPER_ADMIN_NUDGE: super_admin_nudge,
    COMMUNITY_ADMIN_NUDGE: send_events_nudge,
    ADMIN_MOU_NOTIFIER: send_admin_mou_notification,
    USER_EVENT_NUDGE: prepare_user_events_nudge,
    CREATE_COMMUNITY_SNAPSHOTS: create_snapshots,
    POSTMARK_SENDER_SIGNATURE: collect_and_create_signatures,
    PROCESS_CONTENT_SPACING: process_spacing_data,
    UPDATE_ACTION_CONTENT: update_actions_content,
    REMOVE_DUPLICATE_IMAGES: remove_duplicate_images,
    TRANSLATE_DB_CONTENTS: TranslateDBContents().start_translations,
    COMMUNITY_ADMIN_TESTIMONIAL_NUDGE: prepare_testimonials_for_community_admins,
    POSTMARK_NUDGE_REPORT: generate_postmark_nudge_report
}