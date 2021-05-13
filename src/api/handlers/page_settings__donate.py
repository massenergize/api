"""Handler file for all routes pertaining to donate_page_settings"""

from database.models import DonatePageSettings
from api.handlers.page_settings import PageSettingsHandler

class DonatePageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('donate', DonatePageSettings)

