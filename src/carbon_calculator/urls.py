from django.urls import path
from .views import index, ping, info, estimate, reset

urlpatterns = [
    path('',index),
    path('info/<action>', info ),
    path('estimate/<action>', estimate ),
    path('reset', reset )

]