from typing import Tuple
from sentry_sdk import capture_message
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import CustomMassenergizeError, InvalidResourceError, MassEnergizeAPIError
from api.utils.api_utils import create_media_file
from apps__campaigns.models import Technology, TechnologyCoach, TechnologyEvent, TechnologyOverview, TechnologyVendor
from database.models import Event, Media, UserProfile, Vendor
from uuid import UUID
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
                return None, CustomMassenergizeError("Technology does not exist")
            technology.update(**args)
            technology = technology.first()
            if not isinstance(image, str) or not image.startswith("http"):
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
            return technology.first(), None
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
            image = args.pop('image', None)

            technology = Technology.objects.filter(id=technology_id)
            if not technology:
                return None, InvalidResourceError()
            args["technology"] = technology.first()
            

            coach = TechnologyCoach.objects.create(**args)
            
            if image:
                coach.image = create_media_file(image, f"FileUpload for {coach.id} TechnologyCoach")

            coach.save()
        
            return coach, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        


    def remove_technology_coach(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            coach_id = args.pop('id', None)

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
            vendor_ids = args.pop('vendor_ids', None)

            created_list = []


            technology = Technology.objects.filter(id=technology_id).first()
            if not technology:
                return None, InvalidResourceError()
            
            if not vendor_ids:
                return None, InvalidResourceError()
            
            for vendor_id in vendor_ids:
                vendor = Vendor.objects.filter(pk=vendor_id).first()
                tech_vendor, _ = TechnologyVendor.objects.get_or_create(technology=technology, vendor=vendor)
                created_list.append(tech_vendor.simple_json())

            # delete all vendors that are not in the list
            TechnologyVendor.objects.filter(technology=technology).exclude(id__in=[x.get("id") for x in created_list]).delete()
        
            return created_list, None
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
        
    
    def update_technology_coach(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            coach_id = args.pop('id', None)
            image = args.pop('image', None)

            coach = TechnologyCoach.objects.filter(id=coach_id)
            if not coach:
                return None, InvalidResourceError()
            
            if image:
                media = Media.objects.create(file=image, name=f"FileUpload for {coach.first().id} TechnologyCoach")
                coach.first().image = media
            coach.update(**args)
        
            return coach.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        



    def add_technology_events(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            event_ids = args.pop('event_ids', [])

            created_list = []

            technology = Technology.objects.filter(id=technology_id).first()
            if not technology:
                return None, CustomMassenergizeError("technology with id does not exist")
            
            if not event_ids:
                return None, CustomMassenergizeError("event_ids is required")
            
            for event_id in event_ids:
                event = Event.objects.filter(pk=event_id).first()
                tech_event, _ = TechnologyEvent.objects.get_or_create(technology=technology, event=event)
                created_list.append(tech_event.simple_json())

            # delete all events that are not in the list
            TechnologyEvent.objects.filter(technology=technology).exclude(id__in=[x.get("id") for x in created_list]).delete()
        
            return created_list, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        

    def remove_technology_events(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            tech_event_id = args.pop('id', None)

            if not tech_event_id:
                return None, InvalidResourceError()
            
            tech_event = TechnologyEvent.objects.filter(id=tech_event_id).first()
            if not tech_event:
                return None, CustomMassenergizeError("Invalid Technology Event ID")
            
            tech_event.delete()
        
            return tech_event, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        

        

    
