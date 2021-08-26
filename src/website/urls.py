from django.urls import path

from website.views import home, generate_sitemap

urlpatterns = [
  path('', home, name='home'),
  path('sitemap', generate_sitemap, name='generate_sitemap'),
]