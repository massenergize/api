from uuid import UUID
from django.shortcuts import render

from database.models import *
# Create your views here.

#class UserAvatarUpload(APIView):
#    permission_classes = [permissions.IsAuthenticated]
#    parser_classes - [MultiPartParser, FormParser]


def make_UserMediaUpload_for_every_Media(self, request, qs):
    # make_UserMediaUpload_for_Communities()
    make_UserMediaUpload_for_Actions()
    

def make_UserMediaUpload_for_Communities():
    print("IN COMMUNITIES")
   
    community_media = Community.objects.order_by('id').values_list('id', 'logo', 'banner', 'favicon')
    
    for comm_id, logo, banner, favicon in community_media:
        community = Community.objects.get(id = comm_id)

        if UserMediaUpload.objects.filter(media__id = logo).exists():
            media = UserMediaUpload.objects.get(media__id = logo)
            
            if community not in media.communities:
                media.communities.add(community)
            media.is_community_image = True

        elif logo is not None:
            # 'user' field must be UserProfile but Community.owner_email may not be connected to a UserProfile
            # using brad as interim owner for now
            user = UserProfile.objects.get(email = community.owner_email) if UserProfile.objects.filter(email = community.owner_email).exists() else UserProfile.objects.get(email = 'brad@massenergize.org')
            media = Media.objects.get(id = logo)

            new_media = UserMediaUpload(user = user, media = media, is_community_image = True)
            new_media.save()

            new_media.communities.add(community)
            new_media.save()


        if UserMediaUpload.objects.filter(media__id = banner).exists():
            media = UserMediaUpload.objects.get(media__id = banner)
            
            if community not in media.communities:
                media.communities.add(community)
            media.is_community_image = True
        elif banner is not None:
            # 'user' field must be UserProfile but Community.owner_email may not be connected to a UserProfile
            # using brad as interim owner for now
            user = UserProfile.objects.get(email = community.owner_email) if UserProfile.objects.filter(email = community.owner_email).exists() else UserProfile.objects.get(email = 'brad@massenergize.org')
            media = Media.objects.get(id = banner)

            new_media = UserMediaUpload(user = user, media = media, is_community_image = True)
            new_media.save()

            new_media.communities.add(community)
            new_media.save()


        if UserMediaUpload.objects.filter(media__id = favicon).exists():
            media = UserMediaUpload.objects.get(media__id = favicon)
            
            if community not in media.communities:
                media.communities.add(community)
            media.is_community_image = True
        elif favicon is not None:
            # 'user' field must be UserProfile but Community.owner_email may not be connected to a UserProfile
            # using brad as interim owner for now
            user = UserProfile.objects.get(email = community.owner_email) if UserProfile.objects.filter(email = community.owner_email).exists() else UserProfile.objects.get(email = 'brad@massenergize.org')
            media = Media.objects.get(id = favicon)

            new_media = UserMediaUpload(user = user, media = media, is_community_image = True)
            new_media.save()

            new_media.communities.add(community)
            new_media.save()

def make_UserMediaUpload_for_Actions():
    action_media = Action.objects.values_list('community', 'image', 'user')
    print("action media:", list(action_media))

    for comm_id, m_id, user in action_media:
        if m_id is not None:
            community = Community.objects.get(id = comm_id) if comm_id else None

            if UserMediaUpload.objects.filter(media__id = m_id).exists():
                media = UserMediaUpload.objects.get(media__id = m_id)
                
                if community and community not in media.communities.all():
                    media.communities.add(community)
                media.is_action_image = True
            else:
                media = Media.objects.get(id = m_id)
                user = UserProfile.objects.get(id = str(user))

                new_media = UserMediaUpload(user = user, media = media, is_action_image = True)
                new_media.save()

                if community:
                    new_media.communities.add(community)
                    new_media.save()




# MEDIA
# id = models.AutoField(primary_key=True)
# name = models.SlugField(max_length=SHORT_STR_LEN, blank=True)
# file = models.FileField(upload_to="media/")
# media_type = models.CharField(max_length=SHORT_STR_LEN, blank=True)
# is_deleted = models.BooleanField(default=False, blank=True)
# order = models.PositiveIntegerField(default=0, blank=True, null=True)



# USER MEDIA UPLOAD:
# id = models.AutoField(primary_key=True)
# user = models.ForeignKey(
#     UserProfile,
#     null=True,
#     related_name="uploads",
#     on_delete=models.DO_NOTHING,
# )
# communities = models.ManyToManyField(
#     Community,
#     related_name="community_uploads",
# )
# media = models.OneToOneField(
#     Media,
#     null=True,
#     related_name="user_upload",
#     on_delete=models.CASCADE,
# )
# is_universal = BooleanField(
#     default=False
# )  # True value here means image is available to EVERYONE, and EVERY COMMUNITY
# settings = models.JSONField(null=True, blank=True)
# created_at = models.DateTimeField(auto_now_add=True)
# updated_at = models.DateTimeField(auto_now=True)