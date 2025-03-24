from _main_.utils.context import Context
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.route_handler import RouteHandler
from api.decorators import admins_only
from api.services.partner import PartnerService


class PartnerHandler(RouteHandler):
    def __init__(self):
        super().__init__()
        self.service = PartnerService()
        self.registerRoutes()

    def registerRoutes(self):
        self.add("/partners.info", self.info)
        self.add("/partners.create", self.create)
        self.add("/partners.list", self.list)
        self.add("/partners.update", self.update)
        self.add("/partners.delete", self.delete)
        self.add("/partners.listForAdmin", self.list_for_admin)



    def info(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        res, err = self.service.get_partner_info(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    def list(self, request):
        context: Context = request.context
        args: dict = context.args

        res, err = self.service.list_partners(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def create(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("campaign_id", str, is_required=True)
        self.validator.expect("name", str, is_required=True)
        self.validator.expect("phone_number", str, is_required=False)
        self.validator.expect("email", str, is_required=False)
        self.validator.expect("website", str, is_required=False)
        self.validator.expect("logo", "file", is_required=False)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        res, err = self.service.create_partner(context, args)
        if err:
            return err
        
        return MassenergizeResponse(data=res)
    
    @admins_only
    def update(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        self.validator.expect("name", str, is_required=False)
        self.validator.expect("phone_number", str, is_required=False)
        self.validator.expect("email", str, is_required=False)
        self.validator.expect("website", str, is_required=False)
        self.validator.expect("logo", "file", is_required=False)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        res, err = self.service.update_partner(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def delete(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        res, err = self.service.delete_partner(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    def list_for_admin(self, request):
        context: Context = request.context
        args: dict = context.args

        res, err = self.service.list_partners_for_admin(context, args)
        
        if err:
            return err
        
        return MassenergizeResponse(data=res)
