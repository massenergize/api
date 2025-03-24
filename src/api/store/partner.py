

from typing import Tuple

from _main_.utils.massenergize_logger import log
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import CustomMassenergizeError, InvalidResourceError, MassEnergizeAPIError
from api.utils.api_utils import create_media_file
from apps__campaigns.models import Campaign, Partner


class PartnerStore:
    def __init__(self):
        self.name = "Partner Store/DB"

    def get_partner_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            partner_id = args.get("id", None)
            partner = Partner.objects.filter(id=partner_id).first()
            if not partner:
                return None, InvalidResourceError()
            
            return partner, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def list_partners(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            partners = Partner.objects.filter(is_deleted=False)
            return partners, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
    
    def create_partner(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            logo = args.pop('logo', None)
            campaign_id = args.pop('campaign_id', None)
          
            if not campaign_id:
                return None, CustomMassenergizeError("Please provide a campaign_id")
            
            campaign = Campaign.objects.filter(id=campaign_id).first()

            if not campaign:
                return None, CustomMassenergizeError("Invalid campaign_id")


            partner = Partner.objects.create(**args)
            if logo:
                partner.logo = create_media_file(logo, f"partner_logo")

            partner.campaign = campaign
            
            partner.save()
            return partner, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def update_partner(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            partner_id = args.pop('id', None)
            logo = args.pop('logo', None)

            if not partner_id:
                return None, CustomMassenergizeError("Please provide a partner_id")

            partners= Partner.objects.filter(id=partner_id)
            if not partners:
                return None, CustomMassenergizeError("Invalid partner_id")
            
            partners.update(**args)
            
            partner = partners.first()
            if logo:
                partner.logo = create_media_file(logo, f"partner_logo")

            partner.save()
            return partner, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        


    def delete_partner(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            partner_id = args.get('id', None)
            partner = Partner.objects.filter(id=partner_id)
            if not partner:
                return None, CustomMassenergizeError("Invalid partner_id")

            partner.update(is_deleted=True)
            return partner.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def list_partners_for_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            partners = Partner.objects.filter(is_deleted=False)
            return partners, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        