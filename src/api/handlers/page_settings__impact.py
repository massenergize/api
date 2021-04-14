"""Handler file for all routes pertaining to teams_page_settings"""

from database.models import ImpactPageSettings
from api.handlers.page_settings import PageSettingsHandler

class ImpactPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('impact', ImpactPageSettings)
