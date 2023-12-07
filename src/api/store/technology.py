from typing import Tuple
from sentry_sdk import capture_message
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import CustomMassenergizeError, InvalidResourceError, MassEnergizeAPIError
from apps__campaigns.models import Technology, TechnologyCoach, TechnologyOverview, TechnologyVendor, Vendor
from database.models import Media, UserProfile


class TechnologyStore:
    def __init__(self):
        self.name = "Campaign Store/DB"

    def get_technology_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            technology_id = args.get("id", None)
            technology = Technology.objects.filter(id=technology_id).first()
            if not technology:
                return None, InvalidResourceError()
            
            return technology, None
        
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        
    
    def list_technologies(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            technologies = Technology.objects.filter(is_deleted=False)
            return technologies, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        

    def create_technology(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            image = args.pop('image', None)
            technology = Technology.objects.create(**args)
            if image:
                media = Media.objects.create(file=image, name=f"FileUpload for {technology.id} Technology")
                technology.image = media
            technology.save()
            return technology, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        
    
    def update_technology(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('id', None)
            image = args.pop('image', None)
            technology = Technology.objects.filter(id=technology_id)
            if not technology:
                return None, InvalidResourceError()
            technology.update(**args)
            technology = technology.first()
            if image:
                media = Media.objects.create(file=image, name=f"FileUpload for {technology.id} Technology")
                technology.image = media
            technology.save()
            return technology, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        
    
    def delete_technology(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            technology_id = args.get('id', None)
            technology = Technology.objects.filter(id=technology_id)
            if not technology:
                return None, InvalidResourceError()

            technology.update(is_deleted=True)
            return technology, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        

    def list_technologies_for_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            technologies = Technology.objects.filter(is_deleted=False)
            return technologies, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        

    def add_technology_coach(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            user_id = args.pop('user_id', None)
            community = args.pop('community', None)

            technology = Technology.objects.filter(id=technology_id)
            if not technology:
                return None, InvalidResourceError()
            

            coach = TechnologyCoach()
            coach.technology = technology.first()
            coach.community = community
            if user_id:
                user = UserProfile.objects.filter(id=user_id).first()
                if user:
                   coach.user = user.first()

            coach.save()
        
            return coach, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        


    def remove_technology_coach(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            coach_id = args.pop('technology_coach_id', None)

            if not coach_id:
                return None, InvalidResourceError()
            
            coach = TechnologyCoach.objects.filter(id=coach_id)
            if not coach:
                return None, CustomMassenergizeError("Invalid Technology Coach ID")
            
            coach.update(is_deleted=True)
        
            return coach.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        


    def add_technology_vendor(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            vendor_id = args.pop('vendor_id', None)

            technology = Technology.objects.filter(id=technology_id)
            if not technology:
                return None, InvalidResourceError()
            
            vendor = Vendor.objects.filter(id=vendor_id)
            if not vendor:
                return None, InvalidResourceError()
            
            tech_vendor = TechnologyVendor()
            tech_vendor.technology = technology.first()
            tech_vendor.vendor = vendor.first()
            tech_vendor.save()
        
            return tech_vendor, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        


    def remove_technology_vendor(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            tech_vendor_id = args.pop('technology_vendor_id', None)

            if not tech_vendor_id:
                return None, InvalidResourceError()
            
            tech_vendor = TechnologyVendor.objects.filter(id=tech_vendor_id)
            if not tech_vendor:
                return None, CustomMassenergizeError("Invalid Technology Vendor ID")
            
            tech_vendor.update(is_deleted=True)
        
            return tech_vendor.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        


    def list_technology_vendors(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            tech = args.pop("technology_id")
            vendors = TechnologyVendor.objects.filter(technology__id=tech,is_deleted=False)
            return vendors, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        
    
    def list_technology_coaches(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            tech = args.pop("technology_id")
            coaches = TechnologyCoach.objects.filter(technology__id=tech,is_deleted=False)
            return coaches, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        
    
    def list_technology_overviews(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            tech = args.pop("technology_id")
            overviews = TechnologyOverview.objects.filter(technology__id=tech,is_deleted=False)
            return overviews, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        

    def add_technology_overview(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            image = args.pop('image', None)

            technology = Technology.objects.filter(id=technology_id)
            if not technology:
                return None, InvalidResourceError()
            args["technology"] = technology.first()

            
            tech_overview = TechnologyOverview(**args)

            if image:
                media = Media.objects.create(file=image, name=f"FileUpload for {tech_overview.id} TechnologyOverview")
                tech_overview.image = media
            tech_overview.save()
        
            return tech_overview, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        

    def update_technology_overview(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            tech_overview_id = args.pop('technology_overview_id', None)
            image = args.pop('image', None)

            tech_overview = TechnologyOverview.objects.filter(id=tech_overview_id)
            if not tech_overview:
                return None, InvalidResourceError()
            
            if image:
                media = Media.objects.create(file=image, name=f"FileUpload for {tech_overview.first().id} TechnologyOverview")
                tech_overview.first().image = media
            tech_overview.update(**args)
        
            return tech_overview.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        

    def delete_technology_overview(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            tech_overview_id = args.pop('technology_overview_id', None)

            if not tech_overview_id:
                return None, InvalidResourceError()
            
            tech_overview = TechnologyOverview.objects.filter(id=tech_overview_id)
            if not tech_overview:
                return None, CustomMassenergizeError("Invalid Technology Overview ID")
            
            tech_overview.update(is_deleted=True)
        
            return tech_overview.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        

        

        

    
