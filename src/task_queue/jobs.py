
from task_queue.events_nudge import send_events_report
from task_queue.views import community_admin_nudge, super_admin_nudge

"""
PLEASE NOTE:
 1- Do not update the dictionary keys.
 2- Do not delete dictionary item if there is a task attached to it.

 You can only add new items to the dictionary.
"""
FUNCTIONS = {
    'Super admin nudge':super_admin_nudge,
    "Community Admin nudge":community_admin_nudge,
    "Events Nudge":send_events_report
}