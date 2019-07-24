from django.urls import path
from . import views

app_name = 'carbon_calculator'

urlpatterns = [
    path('', views.index),
    path('test', views.ping),
    path('info/<action>', views.info),
    path('estimate/<action>', views.estimate),
  ]