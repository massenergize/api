"""Handler file for all routes pertaining to testimonials_page_settings"""

from database.models import TestimonialsPageSettings
from api.handlers.page_settings import PageSettingsHandler
from api.services.page_settings import PageSettingsService

class TestimonialsPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('testimonials')
    self.service = PageSettingsService(TestimonialsPageSettings)

