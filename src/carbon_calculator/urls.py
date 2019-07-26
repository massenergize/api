from django.urls import path
from .views import index, ping, info, estimate

app_name = 'carbon_calculator'

urlpatterns = [
    path('', index),
    path('test', ping),
    path('info/<action>', info ),
    path('estimate/<action>', estimate )  ]