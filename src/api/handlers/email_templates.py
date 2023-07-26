"""Handler file for all routes pertaining to email templates"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import super_admins_only
from api.services.email_templates import EmailTemplatesService


class EmailTemplatesHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = EmailTemplatesService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/email.templates.info", self.info) 
    self.add("/email.templates.create", self.create)
    self.add("/email.templates.list", self.list)
    self.add("/email.templates.update", self.update)

  @super_admins_only
  def info(self, request): 
    context: Context = request.context
    args: dict = context.args
    
    # verify the body of the incoming request
    self.validator.expect("id", str, is_required=True)
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    template_info, err = self.service.get_email_template_info(context, args)
    if err:
      return err
    return MassenergizeResponse(data=template_info)


  @super_admins_only
  def create(self, request): 
    context: Context = request.context
    args = context.get_request_body() 
    (self.validator
      .expect("name", str, is_required=False)
      .expect("template_id", str, is_required=False)
    )

    args, err = self.validator.verify(args)
    if err:
      return err

    template_info, err = self.service.create_email_template(context, args)
    if err:
      return err
    return MassenergizeResponse(data=template_info)


  @super_admins_only
  def list(self, request): 
    context: Context = request.context
    args: dict = context.args

    template_info, err = self.service.list_email_templates(context, args)

    if err:
      return err
    return MassenergizeResponse(data=template_info)


  @super_admins_only
  def update(self, request): 
    context: Context = request.context
    args = context.get_request_body() 
    (self.validator
      .expect("name", str, is_required=False)
      .expect("template_id", str, is_required=False)
      .expect("is_deleted", bool, is_required=False)
      .expect("id", str, is_required=True)
    )

    args, err = self.validator.verify(args)
    if err:
      return err
    
    template_info, err = self.service.update_email_template(context, args)
    if err:
      return err      
      
    return MassenergizeResponse(data=template_info)

