"""Handler file for all routes pertaining to organizations_page_settings"""

from database.models import OrganizationsPageSettings
from api.handlers.page_settings import PageSettingsHandler

class OrganizationsPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('organizations', OrganizationsPageSettings)