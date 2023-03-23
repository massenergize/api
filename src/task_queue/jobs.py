
from task_queue.events_nudge import send_events_nudge
from task_queue.views import community_admin_nudge, send_admin_mou_notification, super_admin_nudge

"""
PLEASE NOTE:
 1- Do not update the dictionary keys.
 2- Do not delete dictionary item if there is a task attached to it.
 3- Make sure to wrap your function in try except and return True or False

 You can only add new items to the dictionary.
"""
FUNCTIONS = {
    'Super admin nudge':super_admin_nudge,
    #"Community Admin nudge":community_admin_nudge,
    #"Events Nudge":send_events_report
    "Community Admin nudge":send_events_nudge
    ,"Admin MOU Notifier": send_admin_mou_notification,
}