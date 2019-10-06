from api.utils.constants import API_VERSION

class RouteHandler:
  """
  This class maps routes to views
  """
  def __init__(self):
    self.routes = {}

  def add(self, route: str, view: function) -> bool:
    self.routes[f"/{API_VERSION}/" + path] = view

  def get_routes_to_views(self):
    return self.routes.items()


