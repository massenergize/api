from django.urls import path, re_path
from django.conf.urls import url
from .views import *
from api.handlers.team import TeamHandler
from api.handlers.action import ActionHandler


urlpatterns = []
urlpatterns.extend(TeamHandler().get_routes_to_views())
urlpatterns.extend(ActionHandler().get_routes_to_views())