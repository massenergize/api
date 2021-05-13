"""Handler file for all routes pertaining to actions_page_settings"""

from database.models import ActionsPageSettings
from api.handlers.page_settings import PageSettingsHandler

class ActionsPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('actions', ActionsPageSettings)

