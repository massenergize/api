from _main_.utils.context import Context
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.route_handler import RouteHandler
from api.decorators import admins_only
from api.services.technology import TechnologyService


class TechnologyHandler(RouteHandler):
    def __init__(self):
        super().__init__()
        self.service = TechnologyService()
        self.registerRoutes()

    def registerRoutes(self):
        self.add("/technologies.info", self.info)
        self.add("/technologies.create", self.create)
        self.add("/technologies.list", self.list)
        self.add("/technologies.update", self.update)
        self.add("/technologies.delete", self.delete)

        self.add("/technologies.coaches.create", self.create_technology_coach)
        self.add("/technologies.coaches.update", self.update_technology_coach)
        self.add("/technologies.coaches.remove", self.remove_coach)

        self.add("/technologies.listForAdmin", self.list_for_admin)

        self.add("/technologies.vendors.add", self.add_vendor)
        self.add("/technologies.vendors.create", self.create_new_vendor)
        self.add("/technologies.vendors.update", self.update_new_vendor)
        self.add("/technologies.vendors.remove", self.remove_vendor)
        self.add("/technologies.vendors.list", self.list_vendors)

        self.add("/technologies.overview.create", self.create_overview)
        self.add("/technologies.overview.update", self.update_overview)
        self.add("/technologies.overview.delete", self.delete_overview)
        self.add("/technologies.overview.list", self.list_overviews)

        self.add("/technologies.deals.create", self.create_deal)
        self.add("/technologies.deals.update", self.update_deal)
        self.add("/technologies.deals.delete", self.delete_deal)

        self.add("/technologies.actions.create", self.create_technology_action)
        self.add("/technologies.actions.update", self.update_technology_action)
        self.add("/technologies.actions.delete", self.delete_technology_action)
        
        self.add("/technologies.faqs.create", self.create_technology_faq)
        self.add("/technologies.faqs.update", self.update_technology_faq)
        self.add("/technologies.faqs.delete", self.delete_technology_faq)
        self.add("/technologies.faqs.list", self.list_technology_faqs)

    def info(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        res, err = self.service.get_technology_info(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def list(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_account_id", str, is_required=False)
        args, err = self.validator.verify(args, strict=True)

        if err:
            return err

        res, err = self.service.list_technologies(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def create(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("name", str, is_required=True)
        self.validator.expect("description", str, is_required=True)
        self.validator.expect("image", "file", is_required=False)


        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.create_technology(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def update(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        self.validator.expect("name", str, is_required=False)
        self.validator.expect("description", str, is_required=False)
        self.validator.expect("image", "file", is_required=False)
        self.validator.expect("icon", str, is_required=False)
        self.validator.expect("summary", str, is_required=False)
        self.validator.expect("coaches_section", dict, is_required=False)
        self.validator.expect("deal_section", dict, is_required=False)
        self.validator.expect("vendors_section", dict, is_required=False)
        self.validator.expect("more_info_section", dict, is_required=False)
        self.validator.expect("faq_section", dict, is_required=False)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.update_technology(context, args)
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
        
        res, err = self.service.delete_technology(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def list_for_admin(self, request):
        context: Context = request.context
        args: dict = context.args

        res, err = self.service.list_technologies_for_admin(context, args)  
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def create_technology_coach(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)
        self.validator.expect("full_name", str, is_required=True)
        self.validator.expect("email", str, is_required=False)
        self.validator.expect("community", str, is_required=False)
        self.validator.expect("image", "file", is_required=False)
        self.validator.expect("phone_number", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.add_technology_coach(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def remove_coach(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)

        args, err = self.validator.verify(args)

        if err:
            return err 
        
        res, err = self.service.remove_technology_coach(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def update_technology_coach(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        self.validator.expect("full_name", str, is_required=False)
        self.validator.expect("email", str, is_required=False)
        self.validator.expect("community", str, is_required=False)
        self.validator.expect("image", "file", is_required=False)
        self.validator.expect("phone_number", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.update_technology_coach(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def add_vendor(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)
        self.validator.expect("vendor_ids", list, is_required=True)

        args, err = self.validator.verify(args)

        if err:
            return err 
        
        res, err = self.service.add_technology_vendor(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def remove_vendor(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)
        self.validator.expect("vendor_id", int, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.remove_technology_vendor(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def create_overview(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)
        self.validator.expect("title", str, is_required=True)
        self.validator.expect("description", str, is_required=True)
        self.validator.expect("image", "file", is_required=False)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.create_technology_overview(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def update_overview(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        self.validator.expect("title", str, is_required=False)
        self.validator.expect("description", str, is_required=False)

        args, err = self.validator.verify(args)

        if err:
            return err 
        
        res, err = self.service.update_technology_overview(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def delete_overview(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.delete_technology_overview(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    


    def list_overviews(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.list_technology_overviews(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    def list_vendors(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.list_technology_vendors(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    


    @admins_only
    def create_deal(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)
        self.validator.expect("title", str, is_required=False)
        self.validator.expect("description", str, is_required=False)
        self.validator.expect("link", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.create_technology_deal(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def update_deal(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        self.validator.expect("title", str, is_required=False)
        self.validator.expect("description", str, is_required=False)
        self.validator.expect("link", str, is_required=False)

        args, err = self.validator.verify(args)

        if err:
            return err 
        
        res, err = self.service.update_technology_deal(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def delete_deal(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.delete_technology_deal(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def create_new_vendor(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("name", str, is_required=True)
        self.validator.expect("website", str, is_required=False)
        self.validator.expect("logo", "file", is_required=False)
        self.validator.expect("technology_id", str, is_required=False)
        self.validator.expect("is_published", bool, is_required=False)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err 
        
        res, err = self.service.create_new_vendor_for_technology(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    


    @admins_only
    def update_new_vendor(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)
        self.validator.expect("vendor_id", int, is_required=True)
        self.validator.expect("name", str, is_required=False)
        self.validator.expect("website", str, is_required=False)
        self.validator.expect("logo", "file", is_required=False)

        args, err = self.validator.verify(args)

        if err:
            return err 
        
        res, err = self.service.update_new_vendor_for_technology(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def create_technology_action(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)
        self.validator.expect("title", str, is_required=True)
        self.validator.expect("description", str, is_required=True)
        self.validator.expect("image", "file", is_required=False)
        self.validator.expect("link", str, is_required=False)
        self.validator.expect("link_text", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err
        
        res, err = self.service.create_technology_action(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def update_technology_action(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        self.validator.expect("title", str, is_required=False)
        self.validator.expect("description", str, is_required=False)
        self.validator.expect("image", "file", is_required=False)
        self.validator.expect("link", str, is_required=False)
        self.validator.expect("link_text", str, is_required=False)

        args, err = self.validator.verify(args)

        if err:
            return err
        
        res, err = self.service.update_technology_action(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def delete_technology_action(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err
        
        res, err = self.service.delete_technology_action(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    
    @admins_only
    def create_technology_faq(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)
        self.validator.expect("question", str, is_required=True)
        self.validator.expect("answer", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err
        
        res, err = self.service.create_technology_faq(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    
    @admins_only
    def update_technology_faq(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        self.validator.expect("question", str, is_required=False)
        self.validator.expect("answer", str, is_required=False)

        args, err = self.validator.verify(args)

        if err:
            return err
        
        res, err = self.service.update_technology_faq(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    
    @admins_only
    def delete_technology_faq(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err
        
        res, err = self.service.delete_technology_faq(context, args)
        if err:
            return err
        return MassenergizeResponse(data=res)
    
    def list_technology_faqs(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        if err:
            return err
        
        res, err = self.service.list_technology_faqs(context, args)
        if err:
            return err
        
        return MassenergizeResponse(data=res)

