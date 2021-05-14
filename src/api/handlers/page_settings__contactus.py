"""Handler file for all routes pertaining to contact_us_page_settings"""

from database.models import ContactUsPageSettings
from api.handlers.page_settings import PageSettingsHandler

class ContactUsPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('contact_us', ContactUsPageSettings)

