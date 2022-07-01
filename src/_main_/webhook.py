

import json
from django.http import HttpResponse
from api.tasks import deactivate_user
from api.utils.constants import GUEST_USER

from database.models import UserProfile
ONE_DAY = 60*60*24

def handle_bounce_webhook(request):
    data = request.body.decode('utf-8')
    email = json.loads(data)['Email']
    user = UserProfile.objects.filter(email=email).first()
    if user:
        user_info = user.user_info.get("user_type")
        if user_info == GUEST_USER:
            deactivate_user.apply_async((user.email,),countdown=ONE_DAY)
    return HttpResponse("OK")