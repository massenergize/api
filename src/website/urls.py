from django.urls import path

from website.views import home

urlpatterns = [
  path('', home, name='home'),
]