from django.contrib import admin
from django.urls import path, include
from .views import *


urlpatterns = [
  path('logout/', logout),
  path('signout/', logout),
  path('login/', login),
  path('signin/', login),
  path('ping', ping),
  path('csrf', csrf)
]
