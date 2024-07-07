from typing import Tuple

from _main_.utils.massenergize_logger import log
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import CustomMassenergizeError, MassEnergizeAPIError
from api.store.utils import get_user_from_context
from apps__campaigns.models import CampaignAccount, CampaignAccountAdmin
from database.models import Community, UserProfile


class CampaignAccountStore:
    def __init__(self):
        self.name = "Campaign Store/DB"


        
    def create_campaign_account(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community_id = args.pop('community_id', None)
            if community_id:
                community = Community.objects.filter(id=community_id).first()
                if not community:
                     return None, CustomMassenergizeError("Community not found!!")
                args['community'] = community

            user = get_user_from_context(context)
            if not user:
                return None, CustomMassenergizeError("User not found")
            args['creator'] = user
            
            account = CampaignAccount.objects.create(**args)
            return account, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
    
    def update_campaign_account(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            account_id = args.pop('id', None)
            if account_id:
                account = CampaignAccount.objects.filter(id=account_id)
                if not account:
                    return None, CustomMassenergizeError("Campaign Account not found!!")
                account.update(**args)
                return account.first(), None
            else:
                return None, CustomMassenergizeError("id not provided")
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def delete_campaign_account(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            account_id = args.get('id', None)
            account = CampaignAccount.objects.filter(id=account_id)
            if not account:
                return None,CustomMassenergizeError("id is required")

            account.update(is_deleted=True)
            return account.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def list_campaign_accounts_for_admins(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            accounts = CampaignAccount.objects.filter(is_deleted=False)
            return accounts, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def get_campaign_account_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            account_id = args.get('id', None)
            account = CampaignAccount.objects.filter(id=account_id)
            if not account:
                return None, CustomMassenergizeError("campaign account not found")

            return account.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def add_admin_to_campaign_account(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            account_id = args.get('id', None)
            user_id = args.get('user_id', None)
            role = args.get('role', None)
            account = CampaignAccount.objects.filter(id=account_id)
            if not account:
                return None, CustomMassenergizeError("campaign account not found")
            
            if not user_id:
                return None, CustomMassenergizeError("user_id is required")
            
            user = UserProfile.objects.filter(id=user_id).first()

            account_admin = CampaignAccountAdmin.objects.create(account=account.first(), user=user, role=role)
            return account_admin, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def remove_admin_from_campaign_account(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            admin_id = args.get('admin_id', None)
            admin = CampaignAccountAdmin.objects.filter(id=admin_id)
            if not admin:
                return None, CustomMassenergizeError("campaign account admin not found")

            admin.update(is_deleted=True)
            return admin.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def update_admin(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            admin_id = args.get('admin_id', None)
            admin = CampaignAccountAdmin.objects.filter(id=admin_id)
            if not admin:
                return None, CustomMassenergizeError("campaign account admin not found")

            admin.update(**args)
            return admin.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

