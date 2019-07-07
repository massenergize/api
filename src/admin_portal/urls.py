from django.urls import path
from .views import *

urlpatterns = [
  path('', home, name='super_admin_home'),
  path('actions', actions, name='super_admin_actions'),
  path('test', test, name='super_admin_test'),
  path(
    'menu/sidebar', 
    get_super_admin_sidebar_menu, 
    name='super_admin_sidebar-menu'
  ),
  path(
    'menu/navbar',
    get_super_admin_navbar_menu,
    name='super_admin_sidebar-menu'
  ),
  path('events', events, name='super_admin_events'),
  path('communities', communities, name='super_admin_communities'),
]