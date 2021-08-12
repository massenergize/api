from django.urls import path

from website import views

urlpatterns = [
  path('', views.communities, name='home'),
  path('communities', views.communities, name='communities'),
  path('community/<slug:subdomain>', views.communities, name='communities'),
  path('actions/<slug:subdomain>', views.communities, name='communities'),
  path('action/<slug:subdomain>', views.communities, name='communities'),
  path('events/<slug:subdomain>', views.communities, name='communities'),
  path('event/<slug:subdomain>', views.communities, name='communities'),
  path('services/<slug:subdomain>', views.communities, name='communities'),
  path('service/<slug:subdomain>', views.communities, name='communities'),
  path('testimonials/<slug:subdomain>', views.communities, name='communities'),
  path('testimonial/<slug:subdomain>', views.communities, name='communities'),
  path('teams/<slug:subdomain>', views.communities, name='communities'),
  path('team/<slug:subdomain>', views.communities, name='communities'),
  path('sitemap', views.generate_sitemap, name='generate_sitemap'),
]