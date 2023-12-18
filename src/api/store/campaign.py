from datetime import datetime
from _main_.utils.common import serialize_all, shorten_url
from api.constants import LOOSED_USER
from api.utils.api_utils import create_media_file
from apps__campaigns.helpers import (
    copy_campaign_data,
    generate_analytics_data,
    generate_campaign_navigation,
    get_campaign_technology_details,
)
from apps__campaigns.models import (
    Campaign,
    CampaignAccount,
    CampaignActivityTracking,
    CampaignCommunity,
    CampaignConfiguration,
    CampaignEvent,
    CampaignFollow,
    CampaignLike,
    CampaignLink,
    CampaignManager,
    CampaignPartner,
    CampaignTechnology,
    CampaignTechnologyLike,
    CampaignTechnologyTestimonial,
    CampaignTechnologyView,
    Comment,
    Partner,
    Technology,
)
from database.models import Community, Event, UserProfile, Media
from _main_.utils.massenergize_errors import (
    MassEnergizeAPIError,
    InvalidResourceError,
    NotAuthorizedError,
    CustomMassenergizeError,
)
from _main_.utils.context import Context
from .utils import get_user_from_context
from django.db.models import Q
from sentry_sdk import capture_message
from typing import Tuple
from django.db.models import Count
from wordfilter import Wordfilter


word_filter = Wordfilter()


class CampaignStore:
    def __init__(self):
        self.name = "Campaign Store/DB"

    def get_campaign_info(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_id = args.get("id", None)
            campaign: Campaign = Campaign.objects.filter(id=campaign_id).first()

            if not campaign:
                return None, CustomMassenergizeError("Invalid Campaign ID")

            return campaign, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_campaigns(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            campaign_account_id = args.get("campaign_account_id", None)
            subdomain = args.get("subdomain", None)

            if campaign_account_id:
                campaigns = Campaign.objects.filter(account__id=campaign_account_id)
            elif subdomain:
                campaigns = Campaign.objects.filter(account__subdomain=subdomain)

            else:
                campaigns = Campaign.objects.filter(
                    Q(owner__id=context.user_id)
                    | Q(owner__email=context.user_email)
                    | Q(is_global=True)
                )

            if not context.is_sandbox:
                if context.user_is_logged_in and not context.user_is_admin():
                    campaigns = campaigns.filter(
                        Q(owner__id=context.user_id) | Q(is_published=True)
                    )
                else:
                    campaigns = campaigns.filter(is_published=True)

            campaigns = campaigns.filter(is_deleted=False).distinct()

            return campaigns, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def create_campaign(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_account_id = args.pop("campaign_account_id", None)
            primary_logo = args.pop("primary_logo", None)
            secondary_logo = args.pop("secondary_logo", None)
            campaign_image = args.pop("campaign_image", None)

            title = args.get("title", None)

            contact_full_name = args.pop("full_name", [])
            contact_email = args.pop("email", None)
            contact_image = args.pop("key_contact_image", None)
            contact_phone = args.pop("phone_number", None)
            if not args.get("start_date", None):
                args["start_date"] = datetime.today()

                print(args)

            owner = get_user_from_context(context)
            if not owner:
               return None, CustomMassenergizeError("User not found")

            if campaign_account_id:
                account = CampaignAccount.objects.get(id=campaign_account_id)
                args["account"] = account

            campaigns = Campaign.objects.filter(
                title=title, owner=owner, is_deleted=False
            )
            if campaigns:
                return campaigns.first(), None

            new_campaign = Campaign.objects.create(**args)
            new_campaign.owner = owner

            new_campaign.primary_logo = create_media_file(
                primary_logo, f"PrimaryLogoFor {title} Campaign"
            )
            new_campaign.secondary_logo = create_media_file(
                secondary_logo, f"SecondaryLogoFor {title} Campaign"
            )
            new_campaign.image = create_media_file(
                campaign_image, f"ImageFor {title} Campaign"
            )

            if contact_email:
                user = UserProfile.objects.filter(email=contact_email).first()
                key_manager = CampaignManager()
                key_manager.is_key_contact = True
                key_manager.campaign = new_campaign
                key_manager.contact = contact_phone
                if user:
                    key_manager.user = user
                else:
                    media = None
                    if contact_image:
                        name = f"ImageFor {contact_email} User"
                        media = Media.objects.create(name=name, file=contact_image)

                    user = UserProfile.objects.create(
                        email=contact_email,
                        full_name=contact_full_name,
                        profile_picture=media,
                    )
                    key_manager.user = user

                key_manager.save()

            new_campaign.save()
            return new_campaign, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_campaigns(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            primary_logo = args.pop("primary_logo", None)
            secondary_logo = args.pop("secondary_logo", None)
            campaign_image = args.pop("campaign_image", None)
            campaign_id = args.pop("id", None)

            campaigns = Campaign.objects.filter(id=campaign_id)
            if not campaigns:
                return None, InvalidResourceError()
            campaign = campaigns.first()

            if not context.user_is_admin():
                args.pop("is_approved", None)
                args.pop("is_published", None)

            if primary_logo:
                args["primary_logo"] = create_media_file(
                    primary_logo, f"PrimaryLogoFor {campaign.title} Campaign"
                )
            if secondary_logo:
                args["secondary_logo"] = create_media_file(
                    secondary_logo, f"SecondaryLogoFor {campaign.title} Campaign"
                )
            if campaign_image:
                args["image"] = create_media_file(
                    campaign_image, f"ImageFor {campaign.title} Campaign"
                )

            campaigns.update(**args)

            return campaign, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def delete_campaign(
        self, context: Context, args
    ) -> Tuple[Campaign, MassEnergizeAPIError]:
        try:
            campaign_id = args.get("id", None)
            if not campaign_id:
                return None, InvalidResourceError()
            # find the action
            campaign_to_delete = Campaign.objects.filter(id=campaign_id).first()
            if not campaign_to_delete:
                return None, InvalidResourceError()

            if (
                not context.user_email == campaign_to_delete.owner.email
                and not context.user_is_super_admin
            ):
                return None, NotAuthorizedError()

            if campaign_to_delete.is_published:
                return None, CustomMassenergizeError("Cannot delete published campaign")
            campaign_to_delete.is_deleted = True
            campaign_to_delete.save()

            return campaign_to_delete, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_campaigns_for_admins(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            campaign_account_id = args.pop("campaign_account_id", None)
            subdomain = args.pop("subdomain", None)

            if context.user_is_super_admin:
                return self.list_campaigns_for_super_admin(context)

            if subdomain:
                campaigns = (
                    Campaign.objects.filter(account__subdomain=subdomain)
                    .select_related("logo")
                    .filter(is_deleted=False)
                )
                return campaigns.distinct(), None

            if campaign_account_id:
                campaigns = (
                    Campaign.objects.filter(account__id=campaign_account_id)
                    .select_related("logo")
                    .filter(is_deleted=False)
                )
                return campaigns.distinct(), None

            campaigns = (
                Campaign.objects.select_related("logo")
                .filter(Q(is_global=True), is_deleted=False)
                .distinct()
            )

            return campaigns, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_campaigns_for_super_admin(self, context: Context):
        try:
            campaigns = Campaign.objects.all().select_related("logo")
            return campaigns.distinct(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def add_campaign_manager(self, context: Context, args):
        try:
            user_ids = args.pop("user_ids", [])
            campaign_id = args.pop("campaign_id", None)

            created_list = []

            if not campaign_id:
                return None, InvalidResourceError()

            campaign = Campaign.objects.filter(id=campaign_id).first()

            if not campaign:
                return None, CustomMassenergizeError("campaign with id not found!")

            if user_ids:
                for user_id in user_ids:
                    user = UserProfile.objects.filter(id=user_id).first()
                    if user:
                        campaign_manager, _ = CampaignManager.objects.get_or_create(
                            campaign=campaign, user=user
                        )
                        created_list.append(campaign_manager.simple_json())

            return created_list, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def remove_campaign_manager(self, context: Context, args):
        try:
            campaign_manager_id = args.pop("campaign_manager_id", None)
            if not campaign_manager_id:
                return None, InvalidResourceError()
            campaign_manager = CampaignManager.objects.filter(
                id=campaign_manager_id
            ).first()
            if not campaign_manager:
                return None, CustomMassenergizeError("campaign with id not found!")

            campaign_manager.is_deleted = True
            campaign_manager.save()

            return campaign_manager, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def add_campaign_community(self, context: Context, args):
        try:
            community_id = args.pop("community_id", None)
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, InvalidResourceError()
            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("campaign with id not found!")

            if not community_id:
                return None, InvalidResourceError()

            community = Community.objects.filter(id=community_id).first()
            if not community:
                return None, CustomMassenergizeError("community with id not found!")

            campaign_community = CampaignCommunity.objects.create(
                campaign=campaign, community=community
            )

            return campaign_community, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def remove_campaign_community(self, context: Context, args):
        try:
            campaign_community_id = args.pop("id", None)
            if not campaign_community_id:
                return None, InvalidResourceError()

            campaign_community = CampaignCommunity.objects.filter(
                id=campaign_community_id
            ).first()
            if not campaign_community:
                return None, CustomMassenergizeError(
                    "campaign Community with id not found!"
                )

            campaign_community.is_deleted = True
            campaign_community.save()

            return campaign_community, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def add_campaign_technology(self, context: Context, args):
        try:
            technology_id = args.pop("technology_id", None)
            campaign_id = args.pop("campaign_id", None)

            if not campaign_id:
                return None, InvalidResourceError()
            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("campaign with id not found!")

            if not technology_id:
                return None, InvalidResourceError()

            technology = Technology.objects.filter(id=technology_id).first()
            if not technology:
                return None, CustomMassenergizeError("technology with id not found!")

            tech, _ = CampaignTechnology.objects.get_or_create(
                campaign=campaign, technology=technology
            )

            return tech, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_campaign_technology(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("id", None)
            deal_section_image = args.pop("deal_section_image", None)
            if not campaign_technology_id:
                return None, InvalidResourceError()

            campaign_technology = CampaignTechnology.objects.filter(
                id=campaign_technology_id
            )
            if not campaign_technology:
                return None, CustomMassenergizeError(
                    "Campaign Technology with id not found!"
                )

            if deal_section_image:
                args["deal_section_image"] = create_media_file(
                    deal_section_image,
                    f"ImageFor {campaign_technology.first().id} CampaignTech",
                )

            campaign_technology.update(**args)

            return campaign_technology.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def remove_campaign_technology(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("id", None)
            if not campaign_technology_id:
                return None, InvalidResourceError()

            campaign_technology = CampaignTechnology.objects.filter(
                id=campaign_technology_id
            ).first()
            if not campaign_technology:
                return None, CustomMassenergizeError(
                    "Campaign Technology with id not found!"
                )

            campaign_technology.is_deleted = True
            campaign_technology.save()

            return campaign_technology, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def create_campaign_technology_testimonial(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            community_id = args.pop("community_id", None)
            image = args.pop("image", None)
            user_id = args.pop("user_id", context.user_id)

            if not campaign_technology_id:
                return None, CustomMassenergizeError(
                    "Campaign Technology ID is required !"
                )

            campaign_technology = CampaignTechnology.objects.filter(
                id=campaign_technology_id
            ).first()
            if not campaign_technology:
                return None, CustomMassenergizeError(
                    "Campaign Technology with id not found!"
                )

            args["campaign_technology"] = campaign_technology

            if not user_id:
                return None, CustomMassenergizeError("User ID is required !")

            user = UserProfile.objects.filter(id=user_id).first()
            if not user:
                return None, CustomMassenergizeError("User with id not found!")

            args["created_by"] = user

            if community_id:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    args["community"] = community

            testimonial, _ = CampaignTechnologyTestimonial.objects.get_or_create(**args)

            if image:
                name = f"ImageFor {testimonial.title} CampaignTech Testimonial"
                media = Media.objects.create(name=name, file=image)
                testimonial.image = media

            testimonial.save()

            return testimonial, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_campaign_technology_testimonial(self, context: Context, args):
        try:
            campaign_technology_testimonial_id = args.pop("id", None)
            community_id = args.pop("community_id", None)
            image = args.pop("image", None)

            if not campaign_technology_testimonial_id:
                return None, InvalidResourceError()

            campaign_technology_testimonials = (
                CampaignTechnologyTestimonial.objects.filter(
                    id=campaign_technology_testimonial_id
                )
            )
            if not campaign_technology_testimonials:
                return None, CustomMassenergizeError(
                    "Campaign Technology testimonial with id not found!"
                )

            campaign_technology_testimonials.update(**args)

            if image:
                name = f"ImageFor {campaign_technology_testimonials.first().title} Campaign"
                media = Media.objects.create(name=name, file=image)
                campaign_technology_testimonials.first().image = media

            if community_id:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    campaign_technology_testimonials.first().community = community

            campaign_technology_testimonials.first().save()

            return campaign_technology_testimonials.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def create_campaign_technology_comment(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            community_id: str = args.pop("community_id", None)
            user_id: str = args.pop("user_id", context.user_id)
            comment_text: str = args.get("text", None)
            word_filter.addWords(["fuck", "pussio"])
            # check for swear words in comment text
            if word_filter.blacklisted(comment_text):
                return None, CustomMassenergizeError(
                    "Comment contains inappropriate language."
                )

            if campaign_technology_id:
                campaign_technology = CampaignTechnology.objects.filter(
                    id=campaign_technology_id
                ).first()
                if campaign_technology:
                    args["campaign_technology"] = campaign_technology

            if not user_id:
                return None, CustomMassenergizeError("User ID is required !")
            user = UserProfile.objects.filter(id=user_id).first()
            if not user:
                return None, CustomMassenergizeError("User with id not found!")
            args["user"] = user

            if community_id:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    args["community"] = community

            comment, _ = Comment.objects.get_or_create(**args)

            latest_comments = Comment.objects.filter(
                campaign_technology__id=campaign_technology_id, is_deleted=False
            ).order_by("-created_at")

            return latest_comments[:20], None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_campaign_technology_comment(self, context: Context, args):
        try:
            comment_id = args.pop("id", None)
            if not comment_id:
                return None, InvalidResourceError()

            comment = Comment.objects.filter(id=comment_id)
            if not comment:
                return None, CustomMassenergizeError("Comment with id not found!")

            comment.update(**args)

            return comment.first(), None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def delete_campaign_technology_comment(self, context: Context, args):
        try:
            comment_id = args.pop("id", None)
            if not comment_id:
                return None, InvalidResourceError()

            comment = Comment.objects.filter(id=comment_id).first()
            if not comment:
                return None, CustomMassenergizeError("Comment with id not found!")

            comment.is_deleted = True
            comment.save()

            return comment, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_campaign_technology_comments(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            if not campaign_technology_id:
                return None, InvalidResourceError()
            comments = Comment.objects.filter(
                campaign_technology__id=campaign_technology_id, is_deleted=False
            )

            return comments, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_campaign_technology_testimonials(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            if not campaign_technology_id:
                return None, InvalidResourceError()
            testimonials = CampaignTechnologyTestimonial.objects.filter(
                campaign_technology__id=campaign_technology_id, is_deleted=False
            )

            return testimonials, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def delete_campaign_technology_testimonial(self, context: Context, args):
        try:
            campaign_technology_testimonial_id = args.pop("id", None)
            if not campaign_technology_testimonial_id:
                return None, InvalidResourceError()

            campaign_technology_testimonial = (
                CampaignTechnologyTestimonial.objects.filter(
                    id=campaign_technology_testimonial_id
                ).first()
            )
            if not campaign_technology_testimonial:
                return None, CustomMassenergizeError(
                    "Campaign Technology testimonial with id not found!"
                )

            campaign_technology_testimonial.is_deleted = True
            campaign_technology_testimonial.save()

            return campaign_technology_testimonial, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_campaign_technologies(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, InvalidResourceError()
            technologies = CampaignTechnology.objects.filter(
                campaign__id=campaign_id, is_deleted=False
            )

            return technologies, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_campaign_communities(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, InvalidResourceError()
            communities = CampaignCommunity.objects.filter(
                campaign__id=campaign_id, is_deleted=False
            )

            return communities, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_campaign_managers(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, InvalidResourceError()
            managers = CampaignManager.objects.filter(
                campaign__id=campaign_id, is_deleted=False
            )

            return managers, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def add_campaign_partners(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            partner_ids = args.pop("partner_ids", None)

            created_list = []

            if not campaign_id:
                return None, InvalidResourceError()

            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("campaign with id not found!")

            if not partner_ids:
                return None, InvalidResourceError()

            for partner_id in partner_ids:
                partner = Partner.objects.filter(id=partner_id).first()
                if partner:
                    campaign_partner, _ = CampaignPartner.objects.get_or_create(
                        campaign=campaign, partner=partner
                    )
                    created_list.append(campaign_partner.to_json())

            return created_list, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def remove_campaign_partners(self, context: Context, args):
        try:
            campaign_partner_id = args.pop("campaign_partner_id", None)
            if not campaign_partner_id:
                return None, InvalidResourceError()

            campaign_partner = CampaignPartner.objects.filter(
                id=campaign_partner_id
            ).first()
            if not campaign_partner:
                return None, CustomMassenergizeError(
                    "Campaign Partner with id not found!"
                )

            campaign_partner.is_deleted = True
            campaign_partner.save()

            return campaign_partner, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_campaign_partners(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, InvalidResourceError()
            partners = CampaignPartner.objects.filter(
                campaign__id=campaign_id, is_deleted=False
            )

            return partners, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def create_campaign_event(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            event_ids = args.pop("event_ids", None)

            created_list = []

            if not campaign_id:
                return None, InvalidResourceError()
            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("campaign with id not found!")

            if not event_ids:
                return None, CustomMassenergizeError("event ids not found!")

            for event_id in event_ids:
                event = Event.objects.filter(id=event_id).first()
                if event:
                    campaign_event, _ = CampaignEvent.objects.get_or_create(
                        campaign=campaign, event=event
                    )
                    created_list.append(campaign_event.simple_json())

            return created_list, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def remove_campaign_event(self, context: Context, args):
        try:
            campaign_event_id = args.pop("campaign_event_id", None)
            if not campaign_event_id:
                return None, InvalidResourceError()

            campaign_event = CampaignEvent.objects.filter(id=campaign_event_id).first()
            if not campaign_event:
                return None, CustomMassenergizeError(
                    "Campaign Event with id not found!"
                )

            campaign_event.is_deleted = True
            campaign_event.save()

            return campaign_event, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def generate_campaign_link(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            utm_source = args.pop("utm_source", None)
            utm_medium = args.pop("utm_medium", None)
            utm_campaign = args.pop("utm_campaign", None)
            url = args.pop("url", None)
            email = args.pop("email", None)

            if not campaign_id:
                return None, InvalidResourceError()

            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign with id not found!")

            campaign_link, _ = CampaignLink.objects.get_or_create(
                campaign=campaign,
                email=email,
                url=url,
                utm_source=utm_source,
                utm_medium=utm_medium,
                utm_campaign=utm_campaign,
            )

            generated_link = f"{url}?utm_source={utm_source}&utm_medium={utm_medium}&campaign_like_id={campaign_link.id}"

            return {"link": shorten_url(generated_link)}, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def campaign_link_visits_count(self, context, args):
        try:
            campaign_link_id = args.pop("campaign_link_id", None)
            if not campaign_link_id:
                return None, InvalidResourceError()

            campaign_link = CampaignLink.objects.filter(id=campaign_link_id).first()
            if campaign_link:
                campaign_link.increase_count()

            return campaign_link, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def add_campaign_follower(self, context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            community_id: str = args.pop("community_id", None)

            email = args.pop("email", None)
            is_other = args.pop("is_other", False)

            if not campaign_id:
                return None, CustomMassenergizeError("Campaign id not found!")

            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign with id not found!")

            if email:
                user, _ = UserProfile.objects.get_or_create(email=email)
                if _:
                    user.user_info = {"user_type": LOOSED_USER}
                    user.save()
                args["user"] = user

            if is_other:
                other_comm, _ = Community.objects.get_or_create(name="Other")
                args["community"] = other_comm
            else:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    args["community"] = community

            follower, _ = CampaignFollow.objects.get_or_create(
                campaign=campaign, **args
            )

            return follower, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def add_campaign_technology_like(self, context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            community_id: str = args.pop("community_id", None)
            user_id: str = args.pop("user_id", None)
            email = args.pop("email", context.user_email)

            if not campaign_technology_id:
                return None, CustomMassenergizeError(
                    "Campaign technology id not found!"
                )

            campaign_technology = CampaignTechnology.objects.filter( id=campaign_technology_id).first()
            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign technology with id not found!")

            if user_id:
                user = UserProfile.objects.filter(id=user_id).first()
                if user:
                    args["user"] = user

            if community_id:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    args["community"] = community

            like, _ = CampaignTechnologyLike.objects.get_or_create(
                campaign_technology=campaign_technology, **args
            )
            if not _:
                if like.is_deleted:
                    like.is_deleted = False
                else:
                    like.is_deleted = True
            like.save()

            campaign_tech = get_campaign_technology_details(campaign_technology_id, False, email)

            return campaign_tech, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def add_campaign_technology_view(self, context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            url = args.pop("url", None)
            if not campaign_technology_id:
                return None, InvalidResourceError()

            campaign_technology = CampaignTechnology.objects.filter(id=campaign_technology_id).first()
            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign technology with id not found!")
            
            link_id = url.split("&campaign_like_id=")
            link_id = link_id[1] if len(link_id) > 1 else None
            
            if link_id:
                campaign_link = CampaignLink.objects.filter(id=link_id).first()
                if campaign_link:
                    campaign_link.increase_count()

            view = CampaignTechnologyView.objects.create(campaign_technology=campaign_technology, **args)
            return view, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_campaign_events(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, InvalidResourceError()
            events = CampaignEvent.objects.filter(
                campaign__id=campaign_id, is_deleted=False
            )

            return events, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def get_campaign_analytics(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, InvalidResourceError()
            campaign = Campaign.objects.filter(id=campaign_id, is_deleted=False).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign with id not found!")
            stats = generate_analytics_data(campaign_id)
            return stats, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
        

    def add_campaign_like(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, InvalidResourceError()

            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign with id not found!")

            like = CampaignLike.objects.create(campaign=campaign, **args)

            return like, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def transfer_ownership(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            new_owner_id = args.pop("user_id", None)
            if not campaign_id:
                return None, InvalidResourceError()

            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign with id not found!")

            new_owner = UserProfile.objects.filter(id=new_owner_id).first()
            if not new_owner:
                return None, CustomMassenergizeError("New owner with id not found!")

            if (
                not context.user_is_super_admin
                and not context.user_id == campaign.owner.id
            ):
                return None, NotAuthorizedError()

            campaign.owner = new_owner
            campaign.save()

            return campaign, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def get_campaign_technology_info(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_technology_id = args.get("campaign_technology_id", None)
            campaign_technology: CampaignTechnology = CampaignTechnology.objects.filter(
                id=campaign_technology_id
            ).first()

            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign Technology not found")

            return campaign_technology, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def get_campaign_technology_testimonial(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_technology_testimonial_id = args.get("id", None)
            campaign_technology_testimonial = (
                CampaignTechnologyTestimonial.objects.filter(
                    id=campaign_technology_testimonial_id
                ).first()
            )

            if not campaign_technology_testimonial:
                return None, CustomMassenergizeError(
                    "Campaign Technology Testimonial not found"
                )

            return campaign_technology_testimonial, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def create_campaign_config(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, InvalidResourceError()

            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign not found")

            config = CampaignConfiguration.objects.create(campaign=campaign, **args)
            return config, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_campaign_config(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_config_id = args.pop("id", None)
            if not campaign_config_id:
                return None, InvalidResourceError()

            campaign_config = CampaignConfiguration.objects.filter(
                id=campaign_config_id
            ).first()
            if not campaign_config:
                return None, CustomMassenergizeError("Campaign Config not found")

            campaign_config.update(**args)
            return campaign_config, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def get_campaign_config(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_config_id = args.get("id", None)
            if not campaign_config_id:
                return None, InvalidResourceError()

            campaign_config = CampaignConfiguration.objects.filter(
                id=campaign_config_id
            ).first()
            if not campaign_config:
                return None, CustomMassenergizeError("Campaign Config not found")

            return campaign_config, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def create_campaign_navigation(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        campaign_id = args.pop("campaign_id", None)

        if not campaign_id:
            return None, CustomMassenergizeError("Campaign id not provided")

        nav = generate_campaign_navigation(campaign_id)
        return nav, None

    def create_campaign_from_template(self, context: Context, args: dict):
        try:
            # template_id = args.pop("template_id", None)
            account_id = args.pop("campaign_account_id", None)
            community_ids = args.pop("community_ids", [])
            title = args.pop("title", None)

            user = get_user_from_context(context)
            if not user:
                return None, CustomMassenergizeError("User not found")

            if not account_id:
                return None, CustomMassenergizeError("Account id not provided")

            if not community_ids:
                return None, CustomMassenergizeError("Community ids not provided")

            if not title:
                return None, CustomMassenergizeError("Title not provided")

            template = Campaign.objects.filter(title="Template Campaign").first()

            if not template:
                return None, CustomMassenergizeError("Campaign Template not found")

            account = CampaignAccount.objects.filter(id=account_id).first()

            new_campaign = Campaign()
            new_campaign.title = title
            new_campaign.account = account
            new_campaign.is_global = False
            new_campaign.is_template = False
            new_campaign.image = template.image
            new_campaign.primary_logo = template.primary_logo
            new_campaign.secondary_logo = template.secondary_logo
            new_campaign.tagline = template.tagline
            new_campaign.description = template.description
            new_campaign.owner = user
            new_campaign.save()

            for community_id in community_ids:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    CampaignCommunity.objects.create(campaign=new_campaign, community=community)

            copy_campaign_data(template, new_campaign)

            return new_campaign, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def track_activity(self, context: Context, args: dict):
        try:
            campaign_id = args.pop("campaign_id", None)

            if not campaign_id:
                return None, CustomMassenergizeError("Campaign ID not provided")
            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign with  ID not found")

            activity = CampaignActivityTracking.objects.create(
                campaign=campaign, **args
            )

            return activity, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
