from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from api.store.task_queue import TaskQueueStore
from _main_.utils.context import Context
from typing import Tuple
from task_queue.jobs import FUNCTIONS


class TaskQueueService:
  """
  Service Layer for all the tasks
  """

  def __init__(self):
    self.store = TaskQueueStore()

  def get_task_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    task, err = self.store.get_task_info(context, args)
    if err:
      return None, err
    return serialize(task, full=True), None

  def list_taks(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    task, err = self.store.list_tasks(context, args)
    if err:
      return None, err
    return serialize_all(task), None

  def list_tasks_funtions(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    functions = list(FUNCTIONS.keys())
    return functions, None


  def create_task(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    task, err = self.store.create_task(context, args)
    if err:
      return None, err
    return serialize(task), None

  def update_task(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    task, err = self.store.update_task(context, args)
    if err:
      return None, err
    return serialize(task), None

  def delete_task(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    task, err = self.store.delete_task(args)
    if err:
      return None, err
    return serialize(task), None


