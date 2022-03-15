"""Handler file for all routes pertaining to auths"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import login_required
from api.services.task_queue import TaskQueueService


class TaskQueueHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = TaskQueueService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/tasks.create", self.create)
    self.add("/tasks.delete", self.delete)
    self.add("/tasks.update", self.update)
    self.add("/tasks.list", self.list_tasks)
    self.add("/tasks.info", self.info)

  @login_required
  def info(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("id", str, is_required=True)

    args, err = self.validator.verify(args)
    if err:
      return err

    team_info, err = self.service.get_task_info(context, args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)


  # @login_required
  def create(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("name", str, is_required=True)
    self.validator.expect("recurring_details", str)
    self.validator.expect("job_name", 'str', is_required=True)
    self.validator.expect("recurring_interval", 'str', is_required=True)
    self.validator.rename("status", "str")

    args, err = self.validator.verify(args)
    if err:
      return err

    task, err = self.service.create_task(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=task)



  def list_tasks(self, request):
    context: Context = request.context
    args: dict = context.args
    tasks, err = self.service.list_taks(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=tasks)



  @login_required
  def update(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("id", int, is_required=True)
    self.validator.expect("name", str, is_required=True)
    self.validator.expect("info", str)
    self.validator.expect("job_name", 'str', is_required=True)
    self.validator.expect("recurring_info", 'str', is_required=True)
    self.validator.rename("status", "str")

    args, err = self.validator.verify(args)
    if err:
      return err

    task, err = self.service.update_task(context, args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=task)

  # @login_required
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    self.validator.expect("id", str, is_required=True)
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    task, err = self.service.delete_task(args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=task)


