from _main_.utils.context import Context
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.route_handler import RouteHandler
from api.services.custom_pages import CustomPagesService


class CustomPagesHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = CustomPagesService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/community.custom.pages.create", self.create_community_custom_page) 
    self.add("/community.custom.pages.update", self.update_community_custom_page)
    self.add("/community.custom.pages.delete", self.delete_community_custom_page)
    self.add("/community.custom.pages.share", self.share_community_custom_page)
    self.add("/community.custom.pages.info", self.community_custom_page_info)
    self.add("/community.custom.pages.list", self.list_community_custom_pages)
    self.add("/custom.page.blocks.create", self.create_custom_page_block)
    self.add("/custom.page.blocks.update", self.update_custom_page_block)
    self.add("/custom.page.blocks.delete", self.delete_custom_page_block)
    self.add("/custom.page.publish", self.publish_custom_page)



  def create_community_custom_page(self, request): 
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("title", str, is_required=True)
    self.validator.expect("community_id", str)

    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    page, err = self.service.create_community_custom_page(context, args)
    if err:
      return err
    return MassenergizeResponse(data=page)
  

  def update_community_custom_page(self, request): 
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("id", str, is_required=True)
    self.validator.expect("title", str, is_required=False)
    self.validator.expect("community_id", str, is_required=False)

    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    page, err = self.service.update_community_custom_page(context, args)
    if err:
      return err
    return MassenergizeResponse(data=page)
  

  def delete_community_custom_page(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("id", str, is_required=True)

    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    page, err = self.service.delete_community_custom_page(context, args)
    if err:
      return err
    return MassenergizeResponse(data=page)
  

  def share_community_custom_page(self, request): 
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("id", str, is_required=True)
    self.validator.expect("audience_ids", "str_list", is_required=True)

    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    page, err = self.service.share_community_custom_page(context, args)
    if err:
      return err
    return MassenergizeResponse(data=page)
  
  
  def community_custom_page_info(self, request): 
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("id", str, is_required=True)

    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    page, err = self.service.community_custom_page_info(context, args)
    if err:
      return err
    return MassenergizeResponse(data=page)
  

  def list_community_custom_pages(self, request): 
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("community_id", "id", is_required=True)

    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    page, err = self.service.list_community_custom_pages(context, args)
    if err:
      return err
    return MassenergizeResponse(data=page)
  

  def create_custom_page_block(self, request): 
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("text", str, is_required=False)
    self.validator.expect("props", dict, is_required=False)
    self.validator.expect("direction", str, is_required=False)
    self.validator.expect("type", str, is_required=False)
    self.validator.expect("order", int, is_required=False)
    self.validator.expect("parent_id", str, is_required=False)
    self.validator.expect("page_id", str, is_required=True)

    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    page_block, err = self.service.create_custom_page_block(context, args)
    if err:
      return err
    return MassenergizeResponse(data=page_block)
  

  def update_custom_page_block(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("id", str, is_required=True)
    self.validator.expect("text", str, is_required=False)
    self.validator.expect("props", dict, is_required=False)
    self.validator.expect("direction", str, is_required=False)
    self.validator.expect("type", str, is_required=False)
    self.validator.expect("order", int, is_required=False)
    self.validator.expect("parent_id", str, is_required=False)
    

    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    page_block, err = self.service.update_custom_page_block(context, args)
    if err:
      return err
    return MassenergizeResponse(data=page_block)
  

  def delete_custom_page_block(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("id", str, is_required=True)

    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    page_block, err = self.service.delete_custom_page_block(context, args)
    if err:
      return err
    return MassenergizeResponse(data=page_block)
  

  def publish_custom_page(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("id", str, is_required=True)

    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    page, err = self.service.publish_custom_page(context, args)
    if err:
      return err
    return MassenergizeResponse(data=page)