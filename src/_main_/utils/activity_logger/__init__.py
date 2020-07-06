import threading
import time
from database.models import ActivityLog
from sentry_sdk import capture_message

class ActivityLogger:

  def __init__(self):
    self.trace = []
    self.request_body = {}
    self.path = None

  
  def add_path(self, path):
    self.path = path

  def add_request_body(self, body):
    #make sure to remove any image or filefield from it
    self.request_body = body

  def add_trace(self, func_name):
    self.trace.append(func_name)

  def save_to_db(self, args):
    try:
      activity = args.pop("activity", None) or args.pop("name", None)
      path = args.pop("path", None)
      user = args.pop("user", None)
      community = args.pop("community", None)
      status = args.pop("status", None)


      activity_log = ActivityLog.objects.create(
        path = self.path,
        user = user, 
        community = community,
        status = status or 'success',
        request_body = self.request_body,
        trace = self.trace
      )
      activity_log.save()
    except Exception as e:
      capture_message(str(e), level="error")
    
      print("Could not log messsage")
  
    
  def log(self, params):
    threading.Thread(target=self.save_to_db, args=(params,)).start()



