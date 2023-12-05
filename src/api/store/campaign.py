from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from api.tests.common import RESET
from apps__campaigns.models import Campaign, CampaignAccount, CampaignManager
from database.models import UserProfile, Media
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, NotAuthorizedError, CustomMassenergizeError
from _main_.utils.context import Context
from .utils import get_user_from_context
from django.db.models import Q
from sentry_sdk import capture_message
from typing import Tuple

class CampaignStore:
  def __init__(self):
    self.name = "Campaign Store/DB"

  def get_Campaign_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      campaign_id = args.get("id", None)
      campaign: Campaign = Campaign.objects.filter(id=campaign_id).first()

      if not campaign:
        return None, InvalidResourceError()
      
      return campaign, None
    
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def list_campaigns(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      campaign_account_id = args.get('campaign_account_id', None)
      subdomain = args.get('subdomain', None)

      if campaign_account_id:
        campaigns = Campaign.objects.select_related('logo').filter(campaign_account__id=campaign_account_id)
      elif subdomain:
        campaigns = Campaign.objects.select_related('logo').filter(campaign_account__subdomain=subdomain)
      else:
        return [], None

      if not context.is_sandbox:
        if context.user_is_logged_in and not context.user_is_admin():
          campaigns = campaigns.filter(Q(owner__id=context.user_id) | Q(is_published=True))
        else:
          campaigns = campaigns.filter(is_published=True)

      campaigns = campaigns.filter(is_deleted=False).distinct()

      return campaigns, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def create_campaign(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      campaign_account_id = args.pop("campaign_account_id", None)
      logo = args.pop('logo', [])
      title = args.pop('title', None)

      contact_full_name = args.pop('full_name', [])
      contact_email = args.pop('email', None)
      contact_image = args.pop('image', None)
      contact_phone = args.get('phone_number', None)

      campaigns = Campaign.objects.filter(title=title, campaign_account__id=campaign_account_id, is_deleted=False)
      if campaigns:
        return campaigns.first(), None

      new_campaign = Campaign.objects.create(**args)

      
      if campaign_account_id:
        account = CampaignAccount.objects.get(id=campaign_account_id)
        new_campaign.account = account

      if logo: #now, images will always come as an array of ids 
        name = f'ImageFor {new_campaign.title} Campaign'
        media = Media.objects.create(name=name, file=logo)
        new_campaign.logo = media


      owner =  get_user_from_context(context)
      if not owner:
         return None, CustomMassenergizeError("User not found")
        
      new_campaign.owner = owner

      
      if contact_email:
        user = UserProfile.objects.filter(email=contact_email).first()
        key_manager = CampaignManager()
        key_manager.is_key_contact = True
        key_manager.campaign = new_campaign
        if user:
          key_manager.user = user
        else:
          media = None
          if contact_image:
            name = f'ImageFor {contact_email} User'
            media = Media.objects.create(name=name, file=contact_image)

          user = UserProfile.objects.create(email=contact_email, full_name=contact_full_name, profile_image=media)
          key_manager.user = user

        key_manager.save()



      new_campaign.save()
      # ----------------------------------------------------------------
      Spy.create_action_footage(actions = [new_campaign], context = context, actor = new_campaign.owner, type = FootageConstants.create(), notes = f"Campaign ID({new_campaign.id})")
      # ----------------------------------------------------------------
      return new_campaign, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)



  def update_campaigns(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      logo = args.pop("logo",)
      campaign_id = args.pop('campaign_id', None)
      campaigns = Campaign.objects.filter(id=campaign_id)
      if not campaigns:
        return None, InvalidResourceError()
      campaign = campaign.first()

      if not context.user_is_admin():
        args.pop("is_approved", None)
        args.pop("is_published", None)

      campaigns.update(**args)


      if logo: 
          if logo[0] == RESET: # reset
            campaign.logo = None
          else:
            media = Media.objects.filter(id = logo[0]).first()
            campaign.logo = media

      campaign.save()
      # ----------------------------------------------------------------
      Spy.create_action_footage(actions = [campaign], context = context, type = FootageConstants.update(), notes =f"Campaign ID({campaign_id})")
      # ----------------------------------------------------------------
      return campaign, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)



  def delete_campaign(self, context: Context, args) -> Tuple[Campaign, MassEnergizeAPIError]:
    try:
      campaign_id = args.get("campaign_id", None)
      if not campaign_id:
        return None, InvalidResourceError()
      #find the action
      campaign_to_delete = Campaign.objects.filter(id=campaign_id).first()
      if not campaign_to_delete:
        return None, InvalidResourceError()

      if not context.user_email == campaign_to_delete.owner.email and not context.user_is_super_admin:
        return None, NotAuthorizedError()
      
      campaign_to_delete.is_deleted = True 
      campaign_to_delete.save()
      # ----------------------------------------------------------------
      Spy.create_action_footage(actions = [campaign_to_delete], context = context,  type = FootageConstants.delete(), notes =f"Deleted Campaign ID({campaign_id})")
      # ----------------------------------------------------------------
      return campaign_to_delete, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def list_campaigns_for_admins(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      campaign_account_id = args.pop("campaign_account_id", None)
      subdomain = args.pop("subdomain", None)

      if context.user_is_super_admin:
        return self.list_campaigns_for_super_admin(context)
      
      if subdomain: 
        campaigns = Campaign.objects.filter(account__subdomain = subdomain).select_related('logo').filter(is_deleted=False)
        return campaigns.distinct(), None
      
      if campaign_account_id:
        campaigns = Campaign.objects.filter(account__id = campaign_account_id).select_related('logo').filter(is_deleted=False)
        return campaigns.distinct(), None
      
      campaigns = Campaign.objects.select_related('logo').filter( Q(is_global=True), is_deleted=False).distinct()
      
      return campaigns, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_campaigns_for_super_admin(self, context: Context):
    # ids = context.args.pop("action_ids",[])
    try:
    #   filter_params = get_actions_filter_params(context.get_params())
      campaigns = Campaign.objects.all().select_related("logo")
      return campaigns.distinct(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


