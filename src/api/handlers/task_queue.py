"""Handler file for all routes pertaining to Task Queue."""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only
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
    self.add("/tasks.functions.list", self.list_tasks_functions)
    self.add("/tasks.info", self.info)
    self.add("/tasks.activate", self.activate)
    self.add("/tasks.deactivate", self.deactivate)

  @admins_only
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

  @admins_only
  def create(self, request):
    context: Context = request.context
    args: dict = context.args


    self.validator.expect("name", str, is_required=True)
    self.validator.expect("recurring_details", str)
    self.validator.expect("job_name", 'str', is_required=True)
    self.validator.expect("frequency", 'str', is_required=True)
    self.validator.expect("status", "str")

    args, err = self.validator.verify(args)
    if err:
      return err
    
    task, err = self.service.create_task(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=task)


  @admins_only
  def list_tasks(self, request):
    context: Context = request.context
    args: dict = context.args
    tasks, err = self.service.list_tasks(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=tasks)

  @admins_only
  def list_tasks_functions(self, request):
    context: Context = request.context
    args: dict = context.args
    tasks, err = self.service.list_tasks_functions(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=tasks)


  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("id", int, is_required=True)
    self.validator.expect("name", 'str', is_required=False)
    self.validator.expect("recurring_details", 'str')
    self.validator.expect("job_name", 'str', is_required=False)
    self.validator.expect("frequency", 'str', is_required=False)
    self.validator.expect("status", 'str', is_required=False)

    args, err = self.validator.verify(args)
    if err:
      return err

    task, err = self.service.update_task(context, args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=task)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args


    self.validator.expect("id", str, is_required=True)
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    task, err = self.service.delete_task(args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=task)


  @admins_only
  def activate(self, request):
    context: Context = request.context
    args: dict = context.args


    self.validator.expect("id", str, is_required=True)
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    task, err = self.service.activate_task(args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=task)



  @admins_only
  def deactivate(self, request):
    context: Context = request.context
    args: dict = context.args


    self.validator.expect("id", str, is_required=True)
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    task, err = self.service.deactivate_task(args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=task)


