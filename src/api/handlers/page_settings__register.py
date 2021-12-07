"""Handler file for all routes pertaining to vendors_page_settings"""

from database.models import RegisterPageSettings
from api.handlers.page_settings import PageSettingsHandler

class RegisterPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('register', RegisterPageSettings)

