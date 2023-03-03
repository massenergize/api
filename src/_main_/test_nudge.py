from django.http import JsonResponse
from task_queue.events_nudge.user_event_nudge import send_user_event_nudge


def test_user_event_nudge(request):
    data = send_user_event_nudge()
    return JsonResponse(data)
