from django.contrib import admin
from django.urls import path

urlpatterns = [
  path(r'',  admin.site.urls),
]
