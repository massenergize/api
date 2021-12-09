from typing import Tuple

from django.core.exceptions import ValidationError
from _main_.utils.utils import Console
from database.models import Community, Media, UserMediaUpload, UserProfile
from django.db.models import Q
import time

limit = 30


class MediaLibraryStore:
    def __init__(self):
        self.name = "MediaLibrary Store/DB"

    def fetch_content(self, args):
        com_ids = args.get("community_ids")
        upper_limit = args.get("upper_limit")
        lower_limit = args.get("lower_limit")
        if not upper_limit and not lower_limit:
            images = Media.objects.filter(
                Q(events__community__id__in=com_ids) # images that are used in events of provided communities
                | Q(actions__community__id__in=com_ids) # images that are used in actions of provided communities
                | Q(testimonials__community__id__in=com_ids) # images that are used in testimonials of provided communities
                | Q(user_upload__communities__id__in=com_ids) # user uploads whose listed communities match the provided communities
                | Q(user_upload__is_universal=True)
            ).order_by("-id")[:limit]
        else:
            images = (
                Media.objects.filter(
                    Q(events__community__id__in=com_ids)
                    | Q(actions__community__id__in=com_ids)
                    | Q(testimonials__community__id__in=com_ids)
                    | Q(user_upload__communities__id__in=com_ids)
                    | Q(user_upload__is_universal=True)
                )
                .exclude(
                    id__gte=lower_limit, id__lte=upper_limit
                )  # exclude content that have already been retrieved
                .order_by("-id")[:limit]
            )
            
        return images, None

    def generateQueryWithScope(self, scope, com_id):
        queries = {
            "actions": Media.objects.filter(actions__community__id=com_id),
            "events": Media.objects.filter(events__community__id=com_id),
            "testimonials": Media.objects.filter(testimonials__community__id=com_id),
            "uploads": Media.objects.filter(user_upload__communities__id=com_id),
            "default": Media.objects.filter(
                Q(events__community__id=com_id)
                | Q(actions__community__id=com_id)
                | Q(testimonials__community__id=com_id)
                | Q(user_upload__communities__id=com_id)
                | Q(user_upload__is_universal=True)
            ),
        }
        query = queries.get(scope)
        if not query:
            query = queries.get("default")
        return query

    def search(self, args):
        com_id = args.get("community_id")
        scope = args.get("scope")
        upper_limit = args.get("upper_limit")
        lower_limit = args.get("lower_limit")
        images = None
        if upper_limit and lower_limit:
            images = (
                self.generateQueryWithScope(scope, com_id)
                .order_by("-id")
                .exclude(id__gte=lower_limit, id__lte=upper_limit)[:limit]
            )
        else:
            images = self.generateQueryWithScope(scope, com_id).order_by("-id")[:limit]
        return images, None

    def remove(self, args):
        media_id = args.get("media_id")
        Media.objects.get(pk=media_id).delete()
        return True, None

    def addToGallery(self, args):
        community_ids = args.get("community_ids")
        user_id = args.get("user_id")
        title = args.get("title") or "Gallery Upload"
        _file = args.get("file")
        is_universal = args.get("is_universal", None)
        communities = user = None
        try:
            if community_ids:
                communities = Community.objects.filter(id__in=community_ids)
            user = UserProfile.objects.get(id=user_id)
        except Community.DoesNotExist:
            return None, "Please provide valid 'community_ids'"
        except UserProfile.DoesNotExist:
            return None, "Please provide a valid 'user_id'"
        except ValidationError:
            return None, "Please provide a valid 'user_id'"
        user_media = self.makeMediaAndSave(
            user=user,
            communities=communities,
            file=_file,
            title=title,
            is_universal=is_universal,
        )
        return (
            user_media,
            None,
        )

    def makeMediaAndSave(self, **kwargs):
        title = kwargs.get("title")
        file = kwargs.get("file")
        user = kwargs.get("user")
        communities = kwargs.get("communities")
        is_universal = kwargs.get("is_universal")
        is_universal = True if is_universal else False
        media = Media.objects.create(
            name=f" {title} - ({round(time.time() * 1000)})",
            file=file,
        )
        user_media = UserMediaUpload(user=user, media=media, is_universal=is_universal)
        user_media.save()
        if communities:
            user_media.communities.set(communities)
        return user_media

    def getImageInfo(self, args):
        media_id = args.get("media_id")
        media = None
        try:
            media = Media.objects.get(pk=media_id)
        except Media.DoesNotExist:
            return None, "Media could not be found, provide a valid 'media_id'"
        except:
            return (
                None,
                "Sorry, something happened we could not find the media you are looking for",
            )
        return media, None
