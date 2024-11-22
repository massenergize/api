from typing import Tuple
from uuid import UUID
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import CustomMassenergizeError, MassEnergizeAPIError, NotAuthorizedError
from _main_.utils.massenergize_logger import log
from api.store.utils import get_user_from_context
from api.utils.api_utils import create_unique_slug, is_admin_of_community
from database.models import Community, CommunityCustomPage, CommunityCustomPageShare, CustomPage, UserProfile
from database.utils.settings.model_constants.enums import SharingType
from django.db.models import Q


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
            slug = args.pop('slug', None)
            content = args.pop('content', None)

            if not community_id:
                return None, CustomMassenergizeError("Missing community_id")
            
            if not title:
                return None, CustomMassenergizeError("Missing title")
            
            if not user:
                return None, NotAuthorizedError() 

            community = Community.objects.get(id=community_id)
            if not community:
                return None, CustomMassenergizeError("Invalid community_id")
            
            slug = create_unique_slug(title, CustomPage, "slug",user_defined_slug=slug)
            
            page = CustomPage.objects.create(title=title, user=user, slug=slug, content=content)

            community_custom_pages = CommunityCustomPage.objects.create(community=community, custom_page=page)
            
            if audience:
                community_custom_pages.audience.set(audience)
            
            if sharing_type:
                community_custom_pages.sharing_type = sharing_type
        
            community_custom_pages.save()
            
            return community_custom_pages, None
 
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
    def update_community_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            page_id = args.get('id', None)
            title = args.get('title', None)
            audience = args.get('audience', None)
            sharing_type = args.get('sharing_type', None)
            slug = args.get('slug', None)
            content = args.get('content', None)
            community_id = args.get('community_id', None)

            page = CustomPage.objects.filter(id=page_id, is_deleted=False).first()
            if not page and not community_id:
                return None, CustomMassenergizeError("Provide a valid page_id or community_id")
            
            if not page:
                return self.create_community_custom_page(context, args)
            
            community_custom_page = CommunityCustomPage.objects.get(custom_page=page)

            if not community_custom_page:
                return None, CustomMassenergizeError("Invalid page_id")
            
            
            if (title and page.title != title) or (slug and page.slug != slug):
                slug = create_unique_slug(title, CustomPage, "slug", user_defined_slug=slug)
                page.title = title

                page.slug = slug
            
            if content:
                page.content = content


            if not is_admin_of_community(context, community_custom_page.community.id):
                return None, NotAuthorizedError() 

            page.save()
            
            if audience:
                community_custom_page.audience.set(audience)
            if sharing_type:
                community_custom_page.sharing_type = sharing_type
        
            community_custom_page.save()
            
            return community_custom_page, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        


    def delete_community_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            page_id = args.pop("id")

            page = CustomPage.objects.get(id=page_id)

            if not page:
                return None, CustomMassenergizeError("Invalid page_id")
            
            community_custom_page = CommunityCustomPage.objects.get(custom_page=page)

            if not community_custom_page:
                return None, CustomMassenergizeError("Invalid page_id")
            
            if not is_admin_of_community(context, community_custom_page.community.id):
                return None, NotAuthorizedError()
            
            community_custom_page.is_deleted = True
            community_custom_page.save()

            page.is_deleted = True
            page.save()

            return page, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def list_community_custom_pages(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community_ids = args.pop('community_ids', None)

            if context.user_is_super_admin:
                community_pages = CommunityCustomPage.objects.filter(is_deleted=False)
                return community_pages, None
            
            user = get_user_from_context(context)
            if not user:
                return None, NotAuthorizedError()
            
            if not community_ids:
                admin_groups = user.communityadmingroup_set.all()
                community_ids = [ag.community.id for ag in admin_groups]

            community_pages = CommunityCustomPage.objects.filter(community__id__in=community_ids, is_deleted=False)

            return community_pages, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        


    def community_custom_page_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            page_id = args.pop('id', None)

            if not page_id:
                return None, CustomMassenergizeError("Missing id")
            
            page = CustomPage.objects.get(id=page_id, is_deleted=False)
            if not page:
                return None, CustomMassenergizeError("Invalid id")
            
            community_custom_page = CommunityCustomPage.objects.get(custom_page=page, is_deleted=False)
            if not community_custom_page:
                return None, CustomMassenergizeError("Invalid id")
            
            return community_custom_page, None
            
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
            
            community_page = CommunityCustomPage.objects.get(id=community_page_id, is_deleted=False)
            if not community_page:
                return None, CustomMassenergizeError("Invalid community_page_id")
            
             
            audience_communities = Community.objects.filter(id__in=audience_communities_id, is_deleted=False)

            page_shares = []
            
            for community_id in audience_communities:
                page_shares.append(
                    CommunityCustomPageShare(
                        community=community_id,
                        community_page=community_page
                    )
                )

            CommunityCustomPageShare.objects.bulk_create(page_shares, ignore_conflicts=True)

            return community_page, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def publish_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            page_id = args.pop('id', None)
            if not page_id:
                return None, CustomMassenergizeError("Missing page_id")
            
            page = CustomPage.objects.get(id=page_id, is_deleted=False)
            if not page:
                return None, CustomMassenergizeError("Invalid page_id")
            
            page.create_version()

            return page, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    def get_custom_pages_for_user_portal(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            page_id = args.pop('id', None)
            if not page_id :
                return None, CustomMassenergizeError("Missing id")
            
            try:
                uuid_id = UUID(page_id, version=4)
                page = CustomPage.objects.filter(id=uuid_id, is_deleted=False).first()
            except ValueError:
                page = CustomPage.objects.filter(slug=page_id, is_deleted=False).first()
         
            if not page:
                return None, CustomMassenergizeError("page not found")
            
            if not page.latest_version:
                return None, CustomMassenergizeError("No version found")

            return  page.latest_version.content, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        

    
    def list_custom_pages_from_other_communities(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community_ids = args.get("community_ids")            
            pages = []
            filters = []
            
            user = get_user_from_context(context)
            
            if not user:
                return None, NotAuthorizedError()
            

            all_community_custom_pages = CommunityCustomPage.objects.filter(is_deleted=False, sharing_type__isnull=False).prefetch_related('community', 'custom_page')


            admin_groups = user.communityadmingroup_set.all()
            admin_of = [ag.community.id for ag in admin_groups]
            
            if community_ids:
                filters.append(Q(community__id__in=community_ids))
            
                
            open_to = Q(sharing_type=SharingType.OPEN_TO.value[0], audience__id__in=admin_of)
            not_closed_to = Q(sharing_type=SharingType.CLOSED_TO.value[0]) & ~Q(audience__id__in=admin_of)
            pages.extend(all_community_custom_pages.filter(Q(sharing_type=SharingType.OPEN.value[0]) | open_to | not_closed_to))
            
            community_pages_list = all_community_custom_pages.filter(id__in=[t.id for t in pages], *filters).exclude(community__id__in=admin_of).distinct()

            pages_list = CustomPage.objects.filter(id__in=[t.custom_page.id for t in community_pages_list], is_deleted=False).distinct()

            
            return pages_list, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        


    def copy_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            page_id = args.pop('page_id', None) 
            community_id = args.pop('community_id', None)
            user = get_user_from_context(context)
            if not user:
                return None, NotAuthorizedError()
            
            if not page_id:
                return None, CustomMassenergizeError("Missing id")
            
            if not community_id:
                return None, CustomMassenergizeError("Missing community_id")
            
            page = CustomPage.objects.get(id=page_id, is_deleted=False)
            if not page:
                return None, CustomMassenergizeError("Invalid id")
            
            community = Community.objects.get(id=community_id, is_deleted=False)
            if not community:
                return None, CustomMassenergizeError("Invalid community_id")

            community_custom_page = CommunityCustomPage.objects.filter(custom_page=page).first()

            new_page = CustomPage.objects.create(
                title=page.title,
                user=user,
                slug=create_unique_slug(page.title, CustomPage),
                content=page.content
            )
            
            community_custom_page = CommunityCustomPage.objects.create(
                community=community,
                custom_page=new_page,
                sharing_type = community_custom_page.sharing_type
            )
            if community_custom_page.audience:
                community_custom_page.audience.set(community_custom_page.audience.all())
            
            return community_custom_page, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        