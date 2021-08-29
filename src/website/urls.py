from django.urls import path

from website import views

urlpatterns = [
  path('', views.home, name='home'),
  path('communities', views.communities, name='communities'),
  path('community/<slug:subdomain>', views.community, name='community'),
  path('actions', views.actions, name='actions'),
  path('action/<int:id>', views.action, name='action'),
  path('events', views.events, name='events'),
  path('event/<int:id>', views.event, name='event'),
  path('services', views.vendors, name='vendors'),
  path('service/<int:id>', views.vendor, name='vendor'),
  path('testimonials', views.testimonials, name='testimonials'),
  path('testimonial/<int:id>', views.testimonial, name='testimonial'),
  path('teams', views.teams, name='teams'),
  path('team/<int:id>', views.team, name='team'),
  path('aboutus', views.about_us, name='about_us'),
  path('donate', views.donate, name='donate'),
  path('contactus', views.contact_us, name='contact_us'),
  path('impact', views.impact, name='impact'),
  path('sitemap', views.generate_sitemap, name='generate_sitemap'),
]