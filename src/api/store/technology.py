from typing import Tuple, Union, Any
from sentry_sdk import capture_message
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import CustomMassenergizeError, InvalidResourceError, MassEnergizeAPIError
from api.utils.api_utils import create_media_file
from apps__campaigns.models import Technology, TechnologyCoach, TechnologyDeal, TechnologyOverview, TechnologyVendor
from database.models import Media, Vendor
from django.db.models import Q


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
            campaign_account_id = args.get("campaign_account_id", None)
            technologies = Technology.objects.filter(Q(campaign_account_id=campaign_account_id)|Q(user__id=context.user_id), is_deleted=False)
            return technologies.distinct(), None
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

            if image and image != "reset":
                if not (isinstance(image, str)):
                    media = Media.objects.create(file=image, name=f"FileUpload for {technology.id} Technology")
                    technology.image = media
            else:
                technology.image = None
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

            if not technology_id:
                return None, CustomMassenergizeError("technology_id is required")

            technology = Technology.objects.filter(id=technology_id)
            if not technology:
                return None, CustomMassenergizeError("technology with id does not exist")
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
                return None, CustomMassenergizeError("coach_id is required")

            coach = TechnologyCoach.objects.filter(id=coach_id)
            if not coach:
                return None, CustomMassenergizeError("Coach with id does not exist")

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
            print("=== vendor_ids ===", vendor_ids)


            technology = Technology.objects.filter(id=technology_id).first()
            if not technology:
                return None, CustomMassenergizeError("technology with id does not exist")
            
            if not vendor_ids:
                return None, CustomMassenergizeError("vendor_ids is required")
            
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
        


    def remove_technology_vendor(self, context: Context, args) -> tuple[TechnologyVendor, MassEnergizeAPIError]:
        try:
            vendor_id = args.pop('vendor_id', None)
            technology_id = args.pop('technology_id', None)

            if not vendor_id:
                return None, CustomMassenergizeError("vendor_id is required")

            if not technology_id:
                return None, CustomMassenergizeError("technology_id is required")
            
            tech_vendor = TechnologyVendor.objects.filter(technology__id=technology_id, vendor__id=vendor_id).first()
            if not tech_vendor:
                return None, CustomMassenergizeError("Technology Vendor with id does not exist")
            
            tech_vendor.delete()
        
            return tech_vendor, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        


    def list_technology_vendors(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            tech = args.pop("technology_id")
            vendors = TechnologyVendor.objects.filter(technology__id=tech, is_deleted=False)
            return vendors, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_technology_coaches(self, context: Context, args) -> Tuple[TechnologyCoach, MassEnergizeAPIError]:
        try:
            tech = args.pop("technology_id")
            coaches = TechnologyCoach.objects.filter(technology__id=tech, is_deleted=False)
            return coaches, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_technology_overviews(self, context: Context, args) -> Tuple[TechnologyOverview, MassEnergizeAPIError]:
        try:
            tech = args.pop("technology_id")
            overviews = TechnologyOverview.objects.filter(technology__id=tech, is_deleted=False)
            return overviews, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def add_technology_overview(self, context: Context, args) -> Tuple[TechnologyOverview, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id')
            image = args.pop('image')

            if not technology_id:
                return None, CustomMassenergizeError("technology_id is required")

            technology = Technology.objects.filter(id=technology_id)
            if not technology:
                return None, CustomMassenergizeError("technology with id does not exist")
            args["technology"] = technology.first()

            
            tech_overview = TechnologyOverview(**args)

            if image and image != "null":
                media = Media.objects.create(file=image, name=f"FileUpload for {tech_overview.id} TechnologyOverview")
                tech_overview.image = media
            tech_overview.save()
        
            return tech_overview, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_technology_overview(self, context: Context, args) -> Tuple[TechnologyOverview, MassEnergizeAPIError]:
        try:
            tech_overview_id = args.pop('id', None)
            image = args.pop('image', None)

            if not tech_overview_id:
                return None, CustomMassenergizeError("id is required")

            tech_overview = TechnologyOverview.objects.filter(id=tech_overview_id)
            if not tech_overview:
                return None, CustomMassenergizeError("Technology Overview does not exist")

            if image != "reset":
                if not isinstance(image, str) or not image.startswith("http"):
                    media = Media.objects.create(file=image,
                                                 name=f"FileUpload for {tech_overview.first().id} TechnologyOverview")
                    args["image"] = media
            else:
                args["image"] = None

            tech_overview.update(**args)

            return tech_overview.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def delete_technology_overview(self, context: Context, args) -> Tuple[TechnologyOverview, MassEnergizeAPIError]:
        try:
            tech_overview_id = args.pop('id', None)

            if not tech_overview_id:
                return None, InvalidResourceError()

            tech_overview = TechnologyOverview.objects.get(id=tech_overview_id)
            if not tech_overview:
                return None, CustomMassenergizeError("Invalid Technology Overview ID")

            tech_overview.delete()

            return tech_overview, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_technology_coach(self, context: Context, args) -> Tuple[TechnologyCoach, MassEnergizeAPIError]:
        try:
            coach_id = args.pop('id', None)
            image = args.pop('image', None)
            if not coach_id:
                return None, CustomMassenergizeError("id is required")

            coach = TechnologyCoach.objects.filter(id=coach_id)
            if not coach:
                return None, CustomMassenergizeError("Coach with id does not exist")

            if image != "reset":
                if not isinstance(image, str):
                    args["image"] = create_media_file(image, f"{coach.first().full_name}")
            else:
                args["image"] = None

            print("== args ==", args)

            coach.update(**args)

            return coach.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def create_technology_deal(self, context: Context, args) -> Tuple[TechnologyDeal, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            if not technology_id:
                return None, CustomMassenergizeError("technology_id is required")
            technology = Technology.objects.filter(id=technology_id).first()
            if not technology:
                return None, CustomMassenergizeError("technology with id does not exist")
            args["technology"] = technology
            technology_deal = TechnologyDeal.objects.create(**args)

            return technology_deal, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_technology_deal(self, context: Context, args) -> Tuple[TechnologyDeal, MassEnergizeAPIError]:
        try:
            technology_deal_id = args.pop('id', None)
            if not technology_deal_id:
                return None, CustomMassenergizeError("id is required")
            technology_deal = TechnologyDeal.objects.filter(id=technology_deal_id)
            if not technology_deal:
                return None, CustomMassenergizeError("Technology Deal does not exist")
            technology_deal.update(**args)

            return technology_deal.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def delete_technology_deal(self, context: Context, args) -> Tuple[TechnologyDeal, MassEnergizeAPIError]:
        try:
            technology_deal_id = args.pop('id', None)
            if not technology_deal_id:
                return None, CustomMassenergizeError("id is required")
            technology_deal = TechnologyDeal.objects.get(id=technology_deal_id)
            if not technology_deal:
                return None, CustomMassenergizeError("Invalid Technology Deal ID")
            technology_deal.delete()

            return technology_deal, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
