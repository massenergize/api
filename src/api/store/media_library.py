from functools import reduce
from typing import List
from django.core.exceptions import ValidationError
from database.utils.common import read_image_from_s3
from database.utils.settings.model_constants.user_media_uploads import (
    UserMediaConstants,
)
from api.store.common import calculate_hash_for_bucket_item, generate_hashes, remove_duplicates_and_attach_relations
from _main_.utils.common import serialize
from _main_.utils.common import serialize, serialize_all
from api.store.common import (
    attach_relations_to_media,
    calculate_hash_for_bucket_item,
    create_csv_file,
    find_duplicate_items,
    resolve_relations,
    summarize_duplicates_into_csv,
)
from _main_.utils.massenergize_logger import log
from _main_.utils.context import Context
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from _main_.utils.utils import Console
from .utils import get_admin_communities, unique_media_filename
from _main_.utils.massenergize_errors import CustomMassenergizeError
from database.models import Community, FeatureFlag, Media, Tag, UserMediaUpload, UserProfile
from django.db.models import Q
import time
from django.http import HttpResponse
from _main_.settings import IS_LOCAL
import time


limit = 32


class MediaLibraryStore:
    def __init__(self):
        self.name = "MediaLibrary Store/DB"

    def read_image(self, args):
        try:
            id = args.get("media_id", None)
            image = Media.objects.filter(pk=id).get()
            string = read_image_from_s3(image.file.name)
            return string, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def print_duplicates(self, args, context: Context):
        grouped_dupes = find_duplicate_items(False,**args)
        filename = "Summary-of-duplicates" 
        csv_file = summarize_duplicates_into_csv(grouped_dupes,filename)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write(csv_file)

        return response, None

    def group_disposable(self, original: dict, disposable: List[int]):
        """This function simply identifies which items in the disposable list share the same image as the original.
        NB: because we initially did not dynamically label uploaded images (many many years ago.. lool) there are many scenarios where a user has  uploaded the same image multiple times and because the image was the same (with name & everything), it always replaced the existing record in the bucket, but under new media records in the database.

        So many duplicate images(media records) still share the same image reference with the original media record. This is why items that share the same image reference as the chosen original need to be identified and grouped.
        Deletion for such records will be treated differently than other duplicates where the images are the same as the original, but are completely
        different uploads in terms of the reference in the s3 bucket. In such cases the images in the s3 bucket will be removed as well!
        """

        media = Media.objects.filter(pk=original.get("id")).first()
        if not media:
            return None, None
        can_delete = Media.objects.filter(pk__in=disposable)
        only_records = []
        with_image = []
        for m in can_delete:
            if m.file.name == media.file.name:
                only_records.append(m)
            else:
                with_image.append(m)

        return only_records, with_image

    def clean_duplicates(self, args, context: Context):
        hash = args.get("hash", None)
        media_after_attaching = remove_duplicates_and_attach_relations(hash)
        return serialize(media_after_attaching, True), None

    def summarize_duplicates(self, args, context: Context):
        grouped_dupes = find_duplicate_items()
        response = {}
        for hash, array in grouped_dupes.items():
            combined = resolve_relations(array)
            response[hash] = combined
        return response, None

    def generate_hashes(self, args, context: Context):
        """
          Goes over all media items in the database and generates hash values for them. 
          It saves the hash value to the media object after that. 
          If an image is corrupted or not valid in the bucket, the hash generation of that particular image will simply fail silently. 

          This route is simply meant to be run once, since there are lots of images in our system that dont have their hash values generated already. 
          All future image uploads will have their hash values generated automatically and saved to the media object. 
          Check the Media model for the modifications on the "save()" function.
      """
        start = time.time()
        generated = generate_hashes()

        end = time.time()
        msg = f"Generated hashes for {generated} items in {end - start} seconds"
        print(msg)

        return msg, None

    def edit_details(self, args, context: Context):
        try:
            id = args.get("user_upload_id")
            media_id = args.get("media_id")

            email = context.user_email
            user_media_upload = UserMediaUpload.objects.get(pk=id)

            if not user_media_upload:
                return None, CustomMassenergizeError(
                    "Sorry, could not find the image  you want to edit"
                )
            if (
                not (user_media_upload.user.email == email)
                and not context.user_is_super_admin
            ):
                return None, CustomMassenergizeError(
                    "You need to be the uploader of the image  or a super admin to make edits"
                )

            copyright_permission = args.get("copyright", "")
            under_age = args.get("underAge", "")
            guardian_info = args.get("guardian_info")
            copyright_att = args.get("copyright_att")
            tags = args.get("tags")
            communities = args.get("community_ids", [])
            publicity = args.get("publicity", None)
            info = {
                **(user_media_upload.info or {}),
                "has_children": under_age,
                "has_copyright_permission": copyright_permission,
                "guardian_info": guardian_info,
                "copyright_att": copyright_att,
                "permission_key": args.get("permission_key", None),
                "permission_notes": args.get("permission_notes", None),
            }
            user_media_upload.info = info
            # user_media_upload.save()
            media = Media.objects.get(pk=media_id)

            if communities:
                communities = Community.objects.filter(id__in=communities)
                user_media_upload.communities.clear()
                user_media_upload.communities.set(communities)

            if publicity:
                user_media_upload.publicity = publicity
            user_media_upload.save()

            if tags:
                media.tags.clear()
                tags = self.proccess_tags(tags)
                media.tags.set(tags)

            media.save()

            # user_media_upload.refresh_from_db()
            return media, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def find_images(self, args, _):
        ids = args.get("ids", [])
        images = Media.objects.filter(pk__in=ids)
        return images, None

    def fetch_content(self, context: Context, args):
        com_ids = args.get("community_ids") or []
        upper_limit = args.get("upper_limit")
        lower_limit = args.get("lower_limit")
        images = None

        if not com_ids:
            if context.user_is_community_admin:
                communities, _ = get_admin_communities(context)
                com_ids = [c.id for c in communities]
            elif context.user_is_super_admin:
                com_ids = [c.id for c in Community.objects.all()]
            else:
                com_ids = []
                
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
            query &= Q(
                tags__in=tags
            )  # If tags exist, it means all other filters & provided tags

        return query

    def make_query_with_communities(self, **kwargs):
        com_ids = kwargs.get("target_communities", [])
        without = [
            Q(actions__isnull=False),
            Q(events__isnull=False),
            Q(testimonials__isnull=False),
            Q(user_upload__isnull=False),
            Q(vender_logo__isnull=False),
        ]
        with_communities = [
            Q(actions__community__id__in=com_ids),
            Q(events__community__id__in=com_ids),
            Q(testimonials__community__id__in=com_ids),
            Q(user_upload__communities__id__in=com_ids),
            Q(vender_logo__communities__id__in=com_ids),
        ]
        query = None
        if not com_ids:
            query = without
        else:
            query = with_communities
        return query

    def get_most_recent(self, args, context: Context):
        """
        When communities are provided, fetch the most recent images attached to
        actions, events, testimonials, vendors, user uploads that are based in any of the communities in the list.

        If no communities are provided, we just pick anything that is used in (actions, events, testimonials etc...)
        Meaning images that are not being used anywhere will not be included in the "most recent" fetches.
        """
        upper_limit = args.get("upper_limit")
        lower_limit = args.get("lower_limit")
        queries = self.make_query_with_communities(**args)
        query = None
        for qObj in queries:
            if not query:
                query = qObj
            else:
                query |= qObj

        count = Media.objects.filter(query).distinct().count()
        if not upper_limit and not lower_limit:
            images = Media.objects.filter(query).distinct().order_by("-id")[:limit]
        else:
            images = (
                Media.objects.filter(query)
                .distinct()
                .exclude(id__gte=lower_limit, id__lte=upper_limit)
                .order_by("-id")[:limit]
            )
        return images, {"total": count}, None

    def get_public_images(self, args):
        upper_limit = args.get("upper_limit")
        lower_limit = args.get("lower_limit")
        count = Media.objects.filter(
            user_upload__publicity=UserMediaConstants.open()
        ).count()
        if not upper_limit and not lower_limit:
            images = Media.objects.filter(
                user_upload__publicity=UserMediaConstants.open()
            ).order_by("-id")[:limit]
        else:
            images = (
                Media.objects.filter(user_upload__publicity=UserMediaConstants.open())
                .exclude(id__gte=lower_limit, id__lte=upper_limit)
                .order_by("-id")[:limit]
            )

        return images, {"total": count}, None

    def search(self, args, context: Context):
        community_ids = args.get("target_communities", [])
        most_recent = args.get("most_recent", False)
        mine = args.get("my_uploads", False)
        other_admins = args.get("user_ids", [])
        other_admins = not mine and other_admins
        search_by_community = not most_recent and community_ids
        keywords = args.get("keywords", [])
        public = args.get("public", False)

        if public:
            return self.get_public_images(args)
        if keywords:
            return self.get_by_keywords(args)

        if most_recent:
            if context.user_is_super_admin:
                return self.get_most_recent(args, context)
            else:
                communities, _ = get_admin_communities(context)
                args["target_communities"] = [c.id for c in communities]
                return self.get_most_recent(args, context)

        if search_by_community:
            return self.get_most_recent(args, context)

        if mine:
            args["user_ids"] = [context.user_id]
            return self.get_uploads_by_user(args)

        if other_admins:
            return self.get_uploads_by_user(args)

        return [], {}, None

    def get_by_keywords(self, args):
        words = args.get("keywords", [])
        queries = self.make_query_with_communities(**args)
        upper_limit = args.get("upper_limit")
        lower_limit = args.get("lower_limit")

        query = None
        for queryObj in queries:
            words_into_q_objects = [Q(tags__name__icontains=word) for word in words]
            objects_linked_by_OR = reduce(lambda q1, q2: q1 | q2, words_into_q_objects)
            queryObj &= objects_linked_by_OR
            if not query:
                query = queryObj
            else:
                query |= queryObj

        count = Media.objects.filter(query).distinct().count()
        if not upper_limit and not lower_limit:
            images = Media.objects.filter(query).distinct().order_by("-id")[:limit]
        else:
            images = (
                Media.objects.filter(query)
                .distinct()
                .exclude(id__gte=lower_limit, id__lte=upper_limit)
                .order_by("-id")[:limit]
            )

        return images, {"total": count}, None

    def get_uploads_by_user(self, args):
        user_ids = args.get("user_ids", [])
        upper_limit = args.get("upper_limit")
        lower_limit = args.get("lower_limit")
        query = Q(user_upload__user__id__in=user_ids)
        count = Media.objects.filter(query).count()
        if upper_limit and lower_limit:
            images = (
                Media.objects.filter(query)
                .exclude(id__gte=lower_limit, id__lte=upper_limit)
                .order_by("-id")[:limit]
            )
        else:
            images = Media.objects.filter(query).order_by("-id")[:limit]

        return images, {"total": count}, None

    def remove(self, args, context):
        media_id = args.get("media_id")
        media = Media.objects.get(pk=media_id)
        # ----------------------------------------------------------------
        Spy.create_media_footage(
            media=[media],
            context=context,
            type=FootageConstants.delete(),
            notes=f"Deleted ID({media_id})",
        )
        # ----------------------------------------------------------------
        media.delete()

        return True, None

    def proccess_tags(self, list_of_string_tags):
        if not list_of_string_tags:
            return []
        created_tags = []

        for tag_name in list_of_string_tags:
            existing_tag = Tag.objects.filter(name__iexact=tag_name).first()
            if existing_tag:
                created_tags.append(existing_tag.id)
            else:
                tag = Tag(name=tag_name)
                tag.save()
                created_tags.append(tag.id)

        return created_tags

    def addToGallery(self, args, context):
        community_ids = args.get("community_ids", [])
        user_id = args.get("user_id")
        title = args.get("title") or "Gallery Upload"
        file = args.get("file")
        tags = args.get("tags", [])
        is_universal = args.get("is_universal", None)
        communities = user = None
        description = args.get("description", None)
        publicity = args.get("publicity", None)
        # ---------------------------------------------
        copyright_permission = args.get("copyright", "")
        under_age = args.get("underAge", "")
        guardian_info = args.get("guardian_info")
        copyright_att = args.get("copyright_att")

        tags = self.proccess_tags(tags)

        info = {
            "size": args.get("size"),
            "size_text": args.get("size_text"),
            "description": description,
            "has_children": under_age,
            "has_copyright_permission": copyright_permission,
            "guardian_info": guardian_info,
            "copyright_att": copyright_att,
            "permission_key": args.get("permission_key", None),
            "permission_notes": args.get("permission_notes", None),
        }

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
            tags=tags,
            info=info,
            publicity=publicity,
        )
        # ----------------------------------------------------------------
        Spy.create_media_footage(
            media=[user_media.media],
            communities=[*community_ids],
            context=context,
            type=FootageConstants.create(),
            notes=f"Media ID({user_media.media.id})",
        )
        # ----------------------------------------------------------------
        return user_media, None

    def makeMediaAndSave(self, **kwargs):
        title = kwargs.get("title")
        file = kwargs.get("file")
        user = kwargs.get("user")
        tags = kwargs.get("tags")
        info = kwargs.get("info")
        publicity = kwargs.get("publicity", None)
        if not publicity:
            publicity = UserMediaConstants.open_to()
        communities = kwargs.get("communities")
        is_universal = kwargs.get("is_universal")
        is_universal = True if is_universal else False

        # tags = Tag.objects.filter(id__in = tags)
        file.name = unique_media_filename(file)

        media = Media.objects.create(
            name=f"{title}-({round(time.time() * 1000)})",
            file=file,
        )
        user_media = UserMediaUpload(
            user=user,
            media=media,
            is_universal=is_universal,
            info=info,
            publicity=publicity,
        )
        user_media.save()
        if media:
            media.tags.set(tags)

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
