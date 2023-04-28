
from task_queue.events_nudge.cadmin_events_nudge import send_events_nudge
from task_queue.events_nudge.user_event_nudge import prepare_user_events_nudge
from task_queue.views import super_admin_nudge, create_snapshots, send_admin_mou_notification

"""
PLEASE NOTE:
 1- Do not update the dictionary keys.
 2- Do not delete dictionary item if there is a task attached to it.
 3- Make sure to wrap your function in try except and return True or False

 You can only add new items to the dictionary.
"""
FUNCTIONS = {
    'Super admin nudge': super_admin_nudge,
    "Community Admin nudge": send_events_nudge,
    "Admin MOU Notifier": send_admin_mou_notification,
    "User Event Nudge": prepare_user_events_nudge,
    "Create Community Snapshots": create_snapshots,
}