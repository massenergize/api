"""Handler file for all routes pertaining to vendors_page_settings"""

from database.models import VendorsPageSettings
from api.handlers.page_settings import PageSettingsHandler
from api.services.page_settings import PageSettingsService

class VendorsPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('vendors')
    self.service = PageSettingsService(VendorsPageSettings)

