from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, CustomMassenergizeError
from _main_.utils.context import Context
from _main_.utils.massenergize_logger import log
from typing import Tuple
from database.models import UserProfile
from task_queue.models import Task


class TaskQueueStore:
  def __init__(self):
    self.name = "Task Store/DB"

  def get_task_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      task_id = args.get("id", None)
      task = Task.objects.filter(id=task_id).first()
      if not task:
        return None, InvalidResourceError()

      return task, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def list_tasks(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
        filter_args = args
        tasks = Task.objects.filter(is_archived=False,is_automatic_task=False, **filter_args)
        return tasks, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def create_task(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      task = Task.objects.create(
        name=args.get("name", None),
        job_name=args.get("job_name", None),
        status=args.get("status", 'PENDING'),
        recurring_details=args.get("recurring_details", None),
        frequency=args.get("frequency", None),
      )
      if context.user_email:
        user = UserProfile.objects.filter(email=context.user_email).first() 
        if user:
          task.creator = user
        task.create_task()
      task.save()

      return task, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(str(e))

  def update_task(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      task_id = args.get('id', None)
      if not task_id:
        return None, InvalidResourceError()

      task = Task.objects.filter(id=task_id)
      if not task.first():
          return None, InvalidResourceError()
      task.update(**args)
      
      task = Task.objects.filter(id=task_id).first()
      task.delete_periodic_task()
      task.create_task()
      return task, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

      

  def delete_task(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      task_id = args["id"]
      task = Task.objects.get(id=task_id)
      if not task:
        return None, InvalidResourceError()
      task.delete()
      return task, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def activate_task(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      task_id = args["id"]
      task = Task.objects.get(id=task_id)
      if not task:
        return None, InvalidResourceError()

      task.start()
      return task, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)



  def deactivate_task(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      task_id = args["id"]
      task = Task.objects.get(id=task_id)
      if not task:
        return None, InvalidResourceError()

      task.stop()
      return task, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

