

from task_queue.views import send_dashbord_ready_msg, send_greeting


FUNCTIONS = {
    'greetings':send_greeting,
    "dashboard_ready":send_dashbord_ready_msg
}