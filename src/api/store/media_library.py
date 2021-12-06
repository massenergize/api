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
        com_id = args.get("community_id")
        upper_limit = args.get("upper_limit")
        lower_limit = args.get("lower_limit")
        if not upper_limit and not lower_limit:
            images = Media.objects.filter(
                Q(events__community__id=com_id)
                | Q(actions__community__id=com_id)
                | Q(testimonials__community__id=com_id)
                | Q(user_upload__community__id=com_id)
            ).order_by("-id")[:limit]
        else:
            images = (
                Media.objects.filter(
                    Q(events__community__id=com_id)
                    | Q(actions__community__id=com_id)
                    | Q(testimonials__community__id=com_id)
                    | Q(user_upload__community__id=com_id)
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
            "uploads": Media.objects.filter(user_upload__community__id=com_id),
            "default": Media.objects.filter(
                Q(events__community__id=com_id)
                | Q(actions__community__id=com_id)
                | Q(testimonials__community__id=com_id)
                | Q(user_upload__community__id=com_id)
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
        community_id = args.get("community_id")
        user_id = args.get("user_id")
        title = args.get("title") or "Gallery Upload"
        _file = args.get("file")
        community = user = None
        try:
            community = Community.objects.get(pk=community_id)
            user = UserProfile.objects.get(id=user_id)
        except Community.DoesNotExist:
            return None, "Please provide a valid 'community_id'"
        except UserProfile.DoesNotExist:
            return None, "Please provide a valid 'user_id'"
        except ValidationError:
            return None, "Please provide a valid 'user_id'"
        user_media = self.makeMediaAndSave(
            user=user, community=community, file=_file, title=title
        )
        return (
            user_media,
            None,
        )

    def makeMediaAndSave(self, **kwargs):
        title = kwargs.get("title")
        file = kwargs.get("file")
        user = kwargs.get("user")
        community = kwargs.get("community")
        media = Media.objects.create(
            name=f" {title} - ({round(time.time() * 1000)})",
            file=file,
        )
        user_media = UserMediaUpload(user=user, media=media, community=community)
        user_media.save()
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
