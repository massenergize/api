"""Handler file for all routes pertaining to about_us_page_settings"""

from database.models import AboutUsPageSettings
from api.handlers.page_settings import PageSettingsHandler

class AboutUsPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('about_us', AboutUsPageSettings)

