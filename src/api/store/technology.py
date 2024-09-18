from typing import Tuple
from _main_.utils.massenergize_logger import log
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import CustomMassenergizeError, MassEnergizeAPIError
from api.store.utils import get_user_from_context
from api.utils.api_utils import create_media_file, create_or_update_section_from_dict
from apps__campaigns.models import Technology, TechnologyAction, TechnologyCoach, TechnologyDeal, TechnologyFaq, \
    TechnologyOverview, TechnologyVendor
from database.models import Media, Vendor
from django.db.models import Q

from apps__campaigns.models import CampaignAccount


class TechnologyStore:
    def __init__(self):
        self.name = "Campaign Store/DB"

    def get_technology_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            technology_id = args.get("id", None)
            technology = Technology.objects.filter(id=technology_id).first()
            if not technology:
                return None, CustomMassenergizeError("Technology does not exist")

            return technology, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_technologies(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            campaign_account_id = args.get("campaign_account_id", None)
            if context.user_is_admin and not campaign_account_id:
                technologies = Technology.objects.filter(is_deleted=False)
                return technologies.distinct(), None
            technologies = Technology.objects.filter(Q(campaign_account_id=campaign_account_id)|Q(user__id=context.user_id), is_deleted=False)
            return technologies.distinct(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def create_technology(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            image = args.pop('image', None)
            campaign_account_id = args.pop('campaign_account_id', None)
            faq_section = args.pop('faq_section', None)
            
            technology = Technology.objects.create(**args)
            if image:
                media = Media.objects.create(file=image, name=f"FileUpload for {technology.id} Technology")
                technology.image = media

            if campaign_account_id:
                account = CampaignAccount.objects.filter(id=campaign_account_id).first()
                technology.campaign_account = account
                
            if faq_section:
                technology.faq_section = create_or_update_section_from_dict(faq_section)

            technology.save()
            
            return technology, None
        
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_technology(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('id', None)
            image = args.pop('image', None)
            faq_section = args.pop('faq_section', None)
            section_media = args.pop('media', None)
            technology = Technology.objects.filter(id=technology_id)
            if not technology:
                return None, CustomMassenergizeError("Technology does not exist")
            # check if the user is the owner of the technology  or a superadmin
            if not context.user_is_admin:
                if technology.first().user.id != context.user_id:
                    return None, CustomMassenergizeError("You are not authorized to perform this action")
            technology.update(**args)
            technology = technology.first()

            if image and not (isinstance(image, str) and image.startswith("http")):
                image = create_media_file(image, f"FileUpload for {technology.id} Technology")
                technology.image = image
                
            if faq_section:
                technology.faq_section = create_or_update_section_from_dict(faq_section, section_media)

            technology.save()
            return technology, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def delete_technology(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            technology_id = args.get('id', None)
            technology = Technology.objects.filter(id=technology_id)
            if not technology:
                return None, CustomMassenergizeError("Technology does not exist")

            if not context.user_is_admin:
                if technology.first().user.id != context.user_id:
                    return None, CustomMassenergizeError("You are not authorized to perform this action")

            technology.update(is_deleted=True)
            return technology.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_technologies_for_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            technologies = Technology.objects.filter(is_deleted=False)
            return technologies, None
        except Exception as e:
            log.exception(e)
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
            log.exception(e)
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
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def add_technology_vendor(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            vendor_ids = args.pop('vendor_ids', None)

            created_list = []
            technology = Technology.objects.filter(id=technology_id).first()
            if not technology:
                return None, CustomMassenergizeError("technology with id does not exist")
            
            if not vendor_ids:
                return None, CustomMassenergizeError("vendor_ids is required")
            
            vendors = Vendor.objects.filter(id__in=vendor_ids)
            for vendor in vendors:
                tech_vendor, _ = TechnologyVendor.objects.get_or_create(technology=technology, vendor=vendor, is_deleted=False)
                created_list.append(tech_vendor.simple_json())  # use append instead of extend

            # delete all vendors that are not in the list
            TechnologyVendor.objects.filter(technology=technology).exclude(vendor__id__in=vendor_ids).delete()

            return created_list, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        


    def remove_technology_vendor(self, context: Context, args) -> Tuple[TechnologyVendor, MassEnergizeAPIError]:
        try:
            vendor_id = args.pop('vendor_id', None)
            technology_id = args.pop('technology_id', None)

            if not vendor_id:
                return None, CustomMassenergizeError("vendor_id is required")

            if not technology_id:
                return None, CustomMassenergizeError("technology_id is required")
            
            tech_vendor = TechnologyVendor.objects.filter(technology__id=technology_id, vendor__id=vendor_id, is_deleted=False).first()
            if not tech_vendor:
                return None, CustomMassenergizeError("Technology Vendor with id does not exist")
            
            tech_vendor.is_deleted = True
            tech_vendor.save()
        
            return tech_vendor, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        


    def list_technology_vendors(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            tech = args.pop("technology_id")
            vendors = TechnologyVendor.objects.filter(technology__id=tech, is_deleted=False)
            return vendors, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_technology_coaches(self, context: Context, args) -> Tuple[TechnologyCoach, MassEnergizeAPIError]:
        try:
            tech = args.pop("technology_id")
            coaches = TechnologyCoach.objects.filter(technology__id=tech, is_deleted=False)
            return coaches, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_technology_overviews(self, context: Context, args) -> Tuple[TechnologyOverview, MassEnergizeAPIError]:
        try:
            tech = args.pop("technology_id")
            overviews = TechnologyOverview.objects.filter(technology__id=tech, is_deleted=False)
            return overviews, None
        except Exception as e:
            log.exception(e)
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
            log.exception(e)
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

            if image and not (isinstance(image, str) and image.startswith("http")):
                image = create_media_file(image, f"FileUpload for {tech_overview.first().title} Overview")
                args["image"] = image

            tech_overview.update(**args)

            return tech_overview.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def delete_technology_overview(self, context: Context, args) -> Tuple[TechnologyOverview, MassEnergizeAPIError]:
        try:
            tech_overview_id = args.pop('id', None)

            if not tech_overview_id:
                return None, CustomMassenergizeError("id is required")

            tech_overview = TechnologyOverview.objects.get(id=tech_overview_id)
            if not tech_overview:
                return None, CustomMassenergizeError("Invalid Technology Overview ID")

            tech_overview.delete()

            return tech_overview, None
        except Exception as e:
            log.exception(e)
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

            if image and not (isinstance(image, str) and image.startswith("http")):
                image = create_media_file(image, f"FileUpload for {coach.first().full_name} coach")
                args["image"] = image

            coach.update(**args)

            return coach.first(), None
        except Exception as e:
            log.exception(e)
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
            log.exception(e)
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
            log.exception(e)
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
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def create_new_vendor_for_technology(self, context: Context, args) -> Tuple[TechnologyVendor, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            user = get_user_from_context(context)
            is_published = args.pop('is_published')

            if not technology_id:
                return None, CustomMassenergizeError("technology_id is required")
            technology = Technology.objects.get(id=technology_id)
            if not technology:
                return None, CustomMassenergizeError("technology with id does not exist")
            vendor = Vendor()
            vendor.name = args.pop('name', None)
            vendor.more_info = {"website": args.pop('website', None), "created_via_campaign": True}
            vendor.logo = create_media_file(args.pop('logo', None), f"FileUpload for {vendor.name} Vendor")
            vendor.user = user
            if is_published:
              vendor.is_published = is_published
            vendor.save()

            technology_vendor, exists = TechnologyVendor.objects.get_or_create(technology=technology, vendor=vendor)

            return technology_vendor, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def update_new_vendor_for_technology(self, context: Context, args) -> Tuple[TechnologyVendor, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            vendor_id = args.pop('vendor_id', None)
            name = args.pop('name', None)
            website = args.pop('website', None)
            logo = args.pop('logo', None)

            if not vendor_id:
                return None, CustomMassenergizeError("vendor_id is required")
            if not technology_id:
                return None, CustomMassenergizeError("technology_id is required")

            technology_vendor = TechnologyVendor.objects.filter(technology__id=technology_id, vendor__id=vendor_id, is_deleted=False).first()
            if not technology_vendor:
                return None, CustomMassenergizeError("technology vendor not found")
            vendor = technology_vendor.vendor
            if name:
                vendor.name = name
            if website:
                more_info = vendor.more_info or {}
                vendor.more_info = {**more_info, "website": website}
            if logo and not (isinstance(logo, str) and logo.startswith("http")):
                logo = create_media_file(logo, f"FileUpload for {vendor.name} vendor")
                vendor.logo = logo
            vendor.save()

            return technology_vendor, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def create_technology_action(self, context: Context, args) -> Tuple[TechnologyAction, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            image = args.pop('image', None)
            if not technology_id:
                return None, CustomMassenergizeError("technology_id is required")
            technology = Technology.objects.get(id=technology_id)
            if not technology:
                return None, CustomMassenergizeError("technology with id does not exist")
            args["technology"] = technology

            image = create_media_file(image, f"FileUpload for {args.get('title')} TechnologyAction")
            args["image"] = image

            technology_action = TechnologyAction.objects.create(**args)

            return technology_action, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
    
    def update_technology_action(self, context: Context, args) -> Tuple[TechnologyAction, MassEnergizeAPIError]:
        try:
            technology_action_id = args.pop('id', None)
            image = args.pop('image', None)
            if not technology_action_id:
                return None, CustomMassenergizeError("id is required")
            technology_action = TechnologyAction.objects.filter(id=technology_action_id)
            if not technology_action:
                return None, CustomMassenergizeError("Technology Action does not exist")
            if image and not (isinstance(image, str) and image.startswith("http")):
                image = create_media_file(image, f"FileUpload for {technology_action.first().title} TechnologyAction")
                args["image"] = image
            technology_action.update(**args)

            return technology_action.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
    
    def delete_technology_action(self, context: Context, args) -> Tuple[TechnologyAction, MassEnergizeAPIError]:
        try:
            technology_action_id = args.pop('id', None)
            if not technology_action_id:
                return None, CustomMassenergizeError("id is required")
            technology_action = TechnologyAction.objects.get(id=technology_action_id)
            if not technology_action:
                return None, CustomMassenergizeError("Invalid Technology Action ID")
            technology_action.delete()

            return technology_action, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
        
    def create_technology_faq(self, context: Context, args) -> Tuple[TechnologyAction, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            
            if not technology_id:
                return None, CustomMassenergizeError("technology_id is required")
            
            technology = Technology.objects.filter(id=technology_id).first()
            
            if not technology:
                return None, CustomMassenergizeError("technology with id does not exist")
            
            args["technology"] = technology

            technology_faq, _ = TechnologyFaq.objects.get_or_create(
                question=args.get('question'),
                answer=args.get('answer'),
                technology=technology
            )

            return technology_faq, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
        
    def update_technology_faq(self, context: Context, args) -> Tuple[TechnologyAction, MassEnergizeAPIError]:
        try:
            technology_faq_id = args.pop('id', None)
            if not technology_faq_id:
                return None, CustomMassenergizeError("id is required")
            
            technology_faq = TechnologyFaq.objects.filter(id=technology_faq_id)
            
            if not technology_faq:
                return None, CustomMassenergizeError("Technology FAQ does not exist")
            
            technology_faq.update(**args)

            return technology_faq.first(), None
        
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
        
    def delete_technology_faq(self, context: Context, args) -> Tuple[TechnologyAction, MassEnergizeAPIError]:
        try:
            technology_faq_id = args.pop('id', None)
            
            if not technology_faq_id:
                return None, CustomMassenergizeError("id is required")
            
            technology_faq = TechnologyFaq.objects.get(id=technology_faq_id)
            
            if not technology_faq:
                return None, CustomMassenergizeError("Invalid Technology FAQ ID")
            
            technology_faq.delete()

            return technology_faq, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
        
    def list_technology_faqs(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            technology_id = args.pop('technology_id', None)
            
            if not technology_id:
                return None, CustomMassenergizeError("technology_id is required")
            
            technology_faqs = TechnologyFaq.objects.filter(technology__id=technology_id)
            
            return technology_faqs, None
        
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
