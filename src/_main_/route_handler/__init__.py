from types import FunctionType as function
from django.urls import path, re_path
from django.conf.urls import url


class RouteHandler:
  """
  This class maps routes to views
  """
  def __init__(self):
    self.routes = {}

  def add(self, route: str, view: function) -> bool:
    path = route[1:]
    self.routes[path] = view

  def get_routes_to_views(self):
    res = []
    for (p, v) in self.routes.items():
      res.append(path(p, v))
    return res



