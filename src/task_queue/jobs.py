
from task_queue.database_tasks.contents_spacing_correction import process_spacing_data
from task_queue.database_tasks.translate_db_content import TranslateDBContents
from task_queue.database_tasks.update_actions_content import update_actions_content
from task_queue.nudges.cadmin_events_nudge import send_events_nudge
from task_queue.nudges.user_event_nudge import prepare_user_events_nudge
from task_queue.nudges.postmark_sender_signature import collect_and_create_signatures
from task_queue.database_tasks.media_library_cleanup import remove_duplicate_images
from task_queue.views import super_admin_nudge, create_snapshots, send_admin_mou_notification

"""
PLEASE NOTE:
 1- Do not update the dictionary keys.
 2- Do not delete dictionary item if there is a task attached to it.
 3- Make sure to wrap your function in try except and return True or False
 4- All tasks from Oct 5th 2023 should have at least one argument(task) which is the task instance.

 You can only add new items to the dictionary.
"""
FUNCTIONS = {
    'Super admin nudge': super_admin_nudge,
    "Community Admin nudge": send_events_nudge,
    "Admin MOU Notifier": send_admin_mou_notification,
    "User Event Nudge": prepare_user_events_nudge,
    "Create Community Snapshots": create_snapshots,
    "Postmark Sender Signature": collect_and_create_signatures,
    "Process Content Spacing": process_spacing_data,
    "Update Action Content": update_actions_content,
    "Remove Duplicate Images": remove_duplicate_images,
    "Translate Database Contents": TranslateDBContents().start_translations
}