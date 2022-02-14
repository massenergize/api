"""Handler file for all routes pertaining to vendors_page_settings"""

from database.models import SigninPageSettings
from api.handlers.page_settings import PageSettingsHandler

class SigninPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('signin', SigninPageSettings)

