"""Handler file for all routes pertaining to teams_page_settings"""

from database.models import TeamsPageSettings
from api.handlers.page_settings import PageSettingsHandler

class TeamsPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('teams', TeamsPageSettings)
