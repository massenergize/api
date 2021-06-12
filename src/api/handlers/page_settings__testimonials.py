"""Handler file for all routes pertaining to testimonials_page_settings"""

from database.models import TestimonialsPageSettings
from api.handlers.page_settings import PageSettingsHandler

class TestimonialsPageSettingsHandler(PageSettingsHandler):

  def __init__(self):
    super().__init__('testimonials', TestimonialsPageSettings)


