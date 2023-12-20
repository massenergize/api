from django.urls import path, include
from website import views

urlpatterns = [
  path('', views.home, name='home'),
  path('campaign/<slug:campaign_id>', views.campaign, name='campaign'),
  path('communities', views.communities, name='communities'),
  path('communities/search/', views.search_communities, name='search_communities'),
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
  path('<slug:subdomain>/home', views.community, name='community'),
  path('<slug:subdomain>/actions', views.actions, name='actions'),
  path('<slug:subdomain>/action/<int:id>', views.action, name='action'),
  path('<slug:subdomain>/events', views.events, name='events'),
  path('<slug:subdomain>/event/<int:id>', views.event, name='event'),
  path('<slug:subdomain>/services', views.vendors, name='vendors'),
  path('<slug:subdomain>/service/<int:id>', views.vendor, name='vendor'),
  path('<slug:subdomain>/testimonials', views.testimonials, name='testimonials'),
  path('<slug:subdomain>/testimonial/<int:id>', views.testimonial, name='testimonial'),
  path('<slug:subdomain>/teams', views.teams, name='teams'),
  path('<slug:subdomain>/team/<int:id>', views.team, name='team'),
  path('<slug:subdomain>/aboutus', views.about_us, name='about_us'),
  path('<slug:subdomain>/donate', views.donate, name='donate'),
  path('<slug:subdomain>/contactus', views.contact_us, name='contact_us'),
  path('<slug:subdomain>/impact', views.impact, name='impact'),
  path('sitemap.xml', views.generate_sitemap_main, name='generate_sitemap_main'),
  path('sitemap', views.generate_sitemap, name='generate_sitemap'),
  path('<slug:subdomain>', views.community, name='community'),
]