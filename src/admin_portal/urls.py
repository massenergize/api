from django.urls import path
from .views import get, post

urlpatterns = [
  path('', get.test, name='test'),
  path('actions', get.community_actions, name='community_actions'),
  path('test', get.test, name='test'),
  path(
    'menu/sidebar', 
    get.get_super_admin_sidebar_menu, 
    name='super-admin-sidebar-menu'
  ),
  path(
    'menu/navbar',
    get.get_super_admin_navbar_menu,
    name='super-admin-sidebar-menu'
  ),
  path('create/action', post.action, name='create_action')
]