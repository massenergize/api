from typing import Tuple
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import CustomMassenergizeError, MassEnergizeAPIError, NotAuthorizedError
from _main_.utils.massenergize_logger import log
from api.store.utils import get_user_from_context
from api.utils.api_utils import create_unique_slug
from database.models import Community, CommunityCustomPage, CommunityCustomPageShare, CustomPage


class CustomPagesStore:
    def __init__(self):
        self.name = "Custom Page Store/DB"

    def create_community_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community_id = args.pop('community_id', None)
            title = args.pop('title', None)
            user = get_user_from_context(context)
            audience = args.pop('audience', None)
            sharing_type = args.pop('sharing_type', None)

            if not community_id:
                return None, CustomMassenergizeError("Missing community_id")
            if not title:
                return None, CustomMassenergizeError("Missing title")
            
            if not user:
                return None, NotAuthorizedError()

            community = Community.objects.get(id=community_id)
            if not community:
                return None, CustomMassenergizeError("Invalid community_id")
            
            slug = create_unique_slug(title, CustomPage, "slug", community.subdomain)
            
            page = CustomPage.objects.create(title=title, user=user, slug=slug)

            community_custom_pages = CommunityCustomPage.objects.create(community=community, page=page)
            
            if audience:
                community_custom_pages.audience.set(audience)
            if sharing_type:
                community_custom_pages.sharing_type = sharing_type
        
            community_custom_pages.save()
            
            return page, None
 
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
    def update_community_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            page_id = args.pop('page_id', None)
            title = args.pop('title', None)
            audience = args.pop('audience', None)
            sharing_type = args.pop('sharing_type', None)

            if not page_id:
                return None, CustomMassenergizeError("Missing page_id")
            if not title:
                return None, CustomMassenergizeError("Missing title")
            

            page = CustomPage.objects.get(id=page_id)
            if not page:
                return None, CustomMassenergizeError("Invalid page_id")
            
            if title and page.title != title:
                slug = create_unique_slug(title, CustomPage, "slug", page.community.subdomain)
                page.slug = slug

            community_custom_page = CommunityCustomPage.objects.get(page=page)
            if not community_custom_page:
                return None, CustomMassenergizeError("Invalid page_id")
            
            if audience:
                community_custom_page.audience.set(audience)
            if sharing_type:
                community_custom_page.sharing_type = sharing_type
        
            community_custom_page.save()
            
            return page, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        


    def delete_community_custom_page(self, context: Context, page_id) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            page = CustomPage.objects.get(id=page_id)
            if not page:
                return None, CustomMassenergizeError("Invalid page_id")
            
            community_custom_page = CommunityCustomPage.objects.get(page=page)
            if not community_custom_page:
                return None, CustomMassenergizeError("Invalid page_id")
            
            community_custom_page.delete()
            page.delete()
            return page, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def list_community_custom_pages(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community_id = args.pop('community_id', None)
            if not community_id:
                return None, CustomMassenergizeError("Missing community_id")
            
            community_pages = CommunityCustomPage.objects.filter(community__id=community_id)
            return community_pages, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        


    def community_custom_page_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            page_id = args.pop('page_id', None)
            if not page_id:
                return None, CustomMassenergizeError("Missing page_id")
            
            page = CustomPage.objects.get(id=page_id)
            if not page:
                return None, CustomMassenergizeError("Invalid page_id")
            
            return page, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
    
    def create_custom_page_block(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            pass

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def update_custom_page_block(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            pass

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
    
    def delete_custom_page_block(self, context: Context, block_id) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            pass

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
    
    def share_community_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community_page_id = args.pop('community_page_id', None)
            audience_communities_id= args.pop('community_ids', None)

            if not community_page_id:
                return None, CustomMassenergizeError("Missing community_page_id")
            if not audience_communities_id:
                return None, CustomMassenergizeError("Missing community_ids")
            
            community_page = CommunityCustomPage.objects.get(id=community_page_id)
            if not community_page:
                return None, CustomMassenergizeError("Invalid community_page_id")
            
             
            audience_communities = Community.objects.filter(id__in=audience_communities_id, is_deleted=False)

            page_shares = []
            
            for community_id in audience_communities:
                page_shares.append(
                    CommunityCustomPageShare(
                        community=community_id,
                        community_custom_page=community_page
                    )
                )

            CommunityCustomPageShare.objects.bulk_create(page_shares)

            return community_page, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def publish_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            page_id = args.pop('page_id', None)
            if not page_id:
                return None, CustomMassenergizeError("Missing page_id")
            
            page = CustomPage.objects.get(id=page_id)
            if not page:
                return None, CustomMassenergizeError("Invalid page_id")
            
            page.create_version()

            return page, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        