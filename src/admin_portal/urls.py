from django.urls import path

from . import views

urlpatterns = [
  path('', views.test, name='test'),
  path('login', views.login, name='login'),
  path('super-admin/menu/sidebar', views.get_super_admin_sidebar_menu, 'super-admin-sidebar-men')
]