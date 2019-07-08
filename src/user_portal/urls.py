from django.urls import path

from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('actions',views.actions, name='actions'),
  path('menu', views.menu, name='menu'),
  path('aboutus', views.aboutUs, name='aboutus'),
  path('events', views.events, name='events'),
  path('stories', views.stories, name='stories')
]