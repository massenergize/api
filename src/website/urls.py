from django.urls import path

from website import views

urlpatterns = [
  path('', views.communities, name='home'),
  path('communities', views.communities, name='communities'),
  path('community/<slug:subdomain>', views.communities, name='communities'),
  path('actions', views.communities, name='communities'),
  path('action/<int:id>', views.communities, name='communities'),
  path('events', views.communities, name='communities'),
  path('event/<int:id>', views.communities, name='communities'),
  path('services', views.communities, name='communities'),
  path('service/<int:id>', views.communities, name='communities'),
  path('testimonials', views.communities, name='communities'),
  path('testimonial/<int:id>', views.communities, name='communities'),
  path('teams', views.communities, name='communities'),
  path('team/<int:id>', views.communities, name='communities'),
  path('events', views.communities, name='communities'),
  path('event/<int:id>', views.communities, name='communities'),
  path('sitemap', views.generate_sitemap, name='generate_sitemap'),
]