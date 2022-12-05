from django.http import JsonResponse
from task_queue.events_nudge import generate_event_for_community


def nudge(request):
    data = generate_event_for_community()
    return JsonResponse({"data":data})