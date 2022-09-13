from django.core.exceptions import ValidationError
from _main_.utils.utils import Console
from .utils import unique_media_filename
from _main_.utils.massenergize_errors import CustomMassenergizeError
from database.models import Community, Media, UserMediaUpload, UserProfile
from django.db.models import Q
import time
import json
limit = 32


class MediaLibraryStore:
    def __init__(self):
        self.name = "MediaLibrary Store/DB"

    def fetch_content(self, args):
        com_ids = args.get("community_ids") or []
        upper_limit = args.get("upper_limit")
        lower_limit = args.get("lower_limit")
        images = None
        if upper_limit and lower_limit:
            images = (
                Media.objects.filter(
                    Q(events__community__id__in=com_ids)
                    | Q(actions__community__id__in=com_ids)
                    | Q(testimonials__community__id__in=com_ids)
                    | Q(user_upload__communities__id__in=com_ids)
                    | Q(user_upload__is_universal=True)
                )
                .distinct()
                .exclude(
                    id__gte=lower_limit, id__lte=upper_limit
                )  # exclude content that have already been retrieved
                .order_by("-id")[:limit]
            )

        else:
            images = (
                Media.objects.filter(
                    Q(
                        events__community__id__in=com_ids
                    )  # images that are used in events of provided communities
                    | Q(
                        actions__community__id__in=com_ids
                    )  # images that are used in actions of provided communities
                    | Q(
                        testimonials__community__id__in=com_ids
                    )  # images that are used in testimonials of provided communities
                    | Q(
                        user_upload__communities__id__in=com_ids
                    )  # user uploads whose listed communities match the provided communities
                    | Q(user_upload__is_universal=True)
                )
                .distinct()
                .order_by("-id")[:limit]
            )

        return images, None

    def generateQueryWithScope(self, **kwargs):
        scope = kwargs.get("scope")
        com_ids = kwargs.get("com_ids", None)
        tags = kwargs.get("tags")
        no_comms_query = {
            "actions": Q(actions__isnull=False),
            "events": Q(events__isnull=False),
            "testimonials": Q(testimonials__isnull=False),
            "uploads": Q(user_upload__isnull=False),
        }
        queries = {
            "actions": Q(actions__community__id__in=com_ids),
            "events": Q(events__community__id__in=com_ids),
            "testimonials": Q(testimonials__community__id__in=com_ids),
            "uploads": Q(user_upload__communities__id__in=com_ids),
        }
        query_object = None
        if com_ids:
            query_object = queries
        else:
            query_object = no_comms_query

        query = query_object.get(scope)
        if tags: 
            query &= Q(tags__in = tags) #If tags exist, it means all other filters & provided tags

        return query

    def search(self, args):
        context = args.get("context")
        com_ids = args.get("target_communities")
        any_community = args.get("any_community")
        filters = args.get("filters",[])
        upper_limit = args.get("upper_limit")
        lower_limit = args.get("lower_limit")
        images = None
        queries = None
        tags = args.get("tags", None)

        """
        Options
        1. No target communities. 
            - Check if user is community_admin, collect images from any community they manage with the provided filters 
            - User is super admin, collect images from any community, with provided filters
        2. User provides target communities, use filters to search for images in the provided target communities
        """
        if any_community == True:
            if context.user_is_community_admin:
                queries = [
                    self.generateQueryWithScope(scope=f, com_ids=com_ids, tags = tags)
                    for f in filters
                ]
            else:
                queries = [self.generateQueryWithScope(scope=f, tags = tags) for f in filters]
        else:
            queries = [
                self.generateQueryWithScope(scope=f, com_ids=com_ids, tags = tags) for f in filters
            ]

        if len(queries) == 0:
            return None, CustomMassenergizeError(
                "Could not build query with your provided filters, please try again"
            )

        query = queries.pop()
        for qObj in queries:
            query |= qObj

        if not upper_limit and not lower_limit:
            images = Media.objects.filter(query).distinct().order_by("-id")[:limit]
        else:
            images = (
                Media.objects.filter(query)
                .distinct()
                .exclude(id__gte=lower_limit, id__lte=upper_limit)
                .order_by("-id")[:limit]
            )
        return images, None

    def remove(self, args):
        media_id = args.get("media_id")
        Media.objects.get(pk=media_id).delete()
        return True, None

    def addToGallery(self, args):
        community_ids = args.get("community_ids")
        user_id = args.get("user_id")
        title = args.get("title") or "Gallery Upload"
        file = args.get("file")

        is_universal = args.get("is_universal", None)
        communities = user = None
        try:
            if community_ids:
                communities = Community.objects.filter(id__in=community_ids)
            user = UserProfile.objects.get(id=user_id)
        except Community.DoesNotExist:
            return None, CustomMassenergizeError("Please provide valid 'community_ids'")
        except UserProfile.DoesNotExist:
            return None, CustomMassenergizeError("Please provide a valid 'user_id'")
        except ValidationError:
            return None, CustomMassenergizeError("Please provide a valid 'user_id'")
        user_media = self.makeMediaAndSave(
            user=user,
            communities=communities,
            file=file,
            title=title,
            is_universal=is_universal,
        )
        return user_media, None

    def makeMediaAndSave(self, **kwargs):
        title = kwargs.get("title")
        file = kwargs.get("file")
        user = kwargs.get("user")
        communities = kwargs.get("communities")
        is_universal = kwargs.get("is_universal")
        is_universal = True if is_universal else False

        file.name = unique_media_filename(file)

        media = Media.objects.create(
            name=f"{title}-({round(time.time() * 1000)})",
            file=file,
        )
        user_media = UserMediaUpload.objects.create(
            user=user, media=media, is_universal=is_universal
        )
        if communities:
            user_media.communities.set(communities)
            user_media.save()
        return user_media

    def getImageInfo(self, args):
        media_id = args.get("media_id")
        media = None
        try:
            media = Media.objects.get(pk=media_id)
        except Media.DoesNotExist:
            return None, CustomMassenergizeError(
                "Media could not be found, provide a valid 'media_id'"
            )
        except:
            return None, CustomMassenergizeError(
                "Sorry, something happened we could not find the media you are looking for"
            )

        return media, None
