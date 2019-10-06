"""Handler file for all routes pertaining to teams"""

from api.utils.route_handler import RouteHandler

class TeamHandler(RouteHandler):

  def registerRoutes(self) -> None:
    self.add("/teams.info", self.info) 


  def info(self) -> None:
    def info_view(request): 
      pass

    return info_view

