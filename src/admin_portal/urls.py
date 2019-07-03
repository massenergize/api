from django.urls import path
from . import views

urlpatterns = [
  path('', views.test, name='test'),
  path('login', views.login, name='login'),
  path(
    'menu/sidebar', 
    views.get_super_admin_sidebar_menu, 
    name='super-admin-sidebar-menu'
  ),
  path(
    'menu/navbar',
    views.get_super_admin_navbar_menu,
    name='super-admin-sidebar-menu'
  ),
  path('create/action', views.create_action, name='create_action')
]