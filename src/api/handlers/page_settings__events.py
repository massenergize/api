"""Handler file for all routes pertaining to events_page_settings"""

from database.models import EventsPageSettings
from api.handlers.page_settings import PageSettingsHandler

class EventsPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('events', EventsPageSettings)

