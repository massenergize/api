
from task_queue.events_nudge import send_events_nudge
from task_queue.events_nudge.user_event_nudge import prepare_user_events_nudge
from task_queue.views import community_admin_nudge, super_admin_nudge, create_time_stamps

#EMMA
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
    "Community Admin nudge":send_events_nudge,
    "User Event Nudge":prepare_user_events_nudge,
    "Create Community Time Stamps": create_time_stamps,
}