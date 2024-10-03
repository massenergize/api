from datetime import datetime
from uuid import UUID
from _main_.utils.common import contains_profane_words, shorten_url
from _main_.utils.constants import CAMPAIGN_URL_ROOT
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.constants import CAMPAIGN_TEMPLATE_KEYS, LOOSED_USER
from api.utils.api_utils import create_media_file, create_or_update_call_to_action_from_dict, \
    create_or_update_section_from_dict
from apps__campaigns.helpers import (
    copy_campaign_data,
    generate_analytics_data,
    generate_campaign_navigation,
    get_campaign_technology_details,
)
from apps__campaigns.models import (
    CallToAction, Campaign,
    CampaignAccount,
    CampaignActivityTracking,
    CampaignCommunity,
    CampaignConfiguration,
    CampaignContact, CampaignFollow,
    CampaignLike,
    CampaignLink,
    CampaignManager,
    CampaignMedia, CampaignPartner,
    CampaignTechnology,
    CampaignTechnologyEvent,
    CampaignTechnologyLike,
    CampaignTechnologyTestimonial,
    CampaignTechnologyView,
    CampaignView,
    Comment,
    Partner,
    Technology,
)
from database.models import Community, Event, Testimonial, UserProfile, Media, Vendor
from _main_.utils.massenergize_errors import (
    MassEnergizeAPIError,
    NotAuthorizedError,
    CustomMassenergizeError,
)
from _main_.utils.context import Context
from .utils import get_user_from_context
from django.db.models import Q
from _main_.utils.massenergize_logger import log
from typing import Tuple
from django.db import transaction

from ..utils.constants import CAMPAIGN_CONTACT_MESSAGE_TEMPLATE, THANK_YOU_FOR_GETTING_IN_TOUCH_TEMPLATE


class CampaignStore:
    def __init__(self):
        self.name = "Campaign Store/DB"

    def get_campaign_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_id = args.get("id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("id is required")

            campaign = None
            try:
                uuid_id = UUID(campaign_id, version=4)
                campaign = Campaign.objects.filter(id=uuid_id, is_deleted=False).first()
            except ValueError:
                campaign = Campaign.objects.filter(slug=campaign_id, is_deleted=False).first()

            if not campaign:
                return None, CustomMassenergizeError("Campaign with id does not exist")

            return campaign, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_campaigns(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            campaign_account_id = args.get("campaign_account_id", None)
            subdomain = args.get("subdomain", None)

            if campaign_account_id:
                campaigns = Campaign.objects.filter(account__id=campaign_account_id)
            elif subdomain:
                campaigns = Campaign.objects.filter(account__subdomain=subdomain)

            else:
                campaigns = Campaign.objects.filter(Q(owner__id=context.user_id)| Q(owner__email=context.user_email)| Q(is_global=True))

            return campaigns.distinct().order_by("-created_at"), None
        except Exception as e:
            log.exception(e)
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

            new_campaign.primary_logo = create_media_file(primary_logo, f"PrimaryLogoFor {title} Campaign")
            new_campaign.secondary_logo = create_media_file(secondary_logo, f"SecondaryLogoFor {title} Campaign")
            new_campaign.image = create_media_file(campaign_image, f"ImageFor {title} Campaign")

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
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_campaigns(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            primary_logo = args.pop("primary_logo", None)
            secondary_logo = args.pop("secondary_logo", None)
            campaign_image = args.pop("campaign_image", None)
            campaign_id = args.pop("id", None)

            banner = args.pop("banner", None)
            section_media = args.pop("media", None)
            goal_section = args.pop("goal_section", None)
            callout_section = args.pop("callout_section", None)
            contact_section = args.pop("contact_section", None)
            call_to_action = args.pop("call_to_action", None)
            banner_section = args.pop("banner_section", None)
            get_in_touch_section = args.pop("get_in_touch_section", None)
            about_us_section = args.pop("about_us_section", None)
            eligibility_section = args.pop("eligibility_section", None)

            campaigns = Campaign.objects.filter(id=campaign_id)
            if not campaigns:
                return None, CustomMassenergizeError("Campaign with id does not exist")

            if not context.user_is_admin():
                args.pop("is_approved", None)
                args.pop("is_published", None)

            if not context.user_is_super_admin:
                if not context.user_email == campaigns.first().owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id, campaign__id=campaign_id)
                    if not campaign_manager:
                        return None, NotAuthorizedError()

            if primary_logo:
                args["primary_logo"] = create_media_file(primary_logo, f"PrimaryLogoFor {campaign_id} Campaign")
            if secondary_logo:
                args["secondary_logo"] = create_media_file(
                    secondary_logo, f"SecondaryLogoFor {campaign_id} Campaign"
                )
            if campaign_image:
                args["image"] = create_media_file(campaign_image, f"ImageFor {campaign_id} Campaign")

            if banner:
                args["banner"] = create_media_file(banner, f"BannerFor {campaign_id} Campaign")

            if goal_section:
                args["goal_section"] = create_or_update_section_from_dict(goal_section, section_media)

            if callout_section:
                args["callout_section"] = create_or_update_section_from_dict(callout_section, section_media)

            if contact_section:
                args["contact_section"] = create_or_update_section_from_dict(contact_section, section_media)

            if call_to_action:
                args["call_to_action"] = create_or_update_call_to_action_from_dict(call_to_action)

            if banner_section:
                args["banner_section"] = create_or_update_section_from_dict(banner_section, section_media)
                
            if get_in_touch_section:
                args["get_in_touch_section"] = create_or_update_section_from_dict(get_in_touch_section, section_media)
            
            if about_us_section:
                args["about_us_section"] = create_or_update_section_from_dict(about_us_section, section_media)
                
            if eligibility_section:
                args["eligibility_section"] = create_or_update_section_from_dict(eligibility_section, section_media)
            campaigns.update(**args)

            return campaigns.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def delete_campaign(
        self, context: Context, args
    ) -> Tuple[Campaign, MassEnergizeAPIError]:
        try:
            campaign_id = args.get("id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("id is required")
            # find the action
            campaign_to_delete = Campaign.objects.filter(id=campaign_id).first()
            if not campaign_to_delete:
                return None, CustomMassenergizeError("Campaign with id does not exist")

            if ( not context.user_email == campaign_to_delete.owner.email and not context.user_is_super_admin):
                return None, NotAuthorizedError()

            if campaign_to_delete.is_published:
                return None, CustomMassenergizeError("Cannot delete published campaign")
            campaign_to_delete.is_deleted = True
            campaign_to_delete.save()

            return campaign_to_delete, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_campaigns_for_admins(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            campaign_account_id = args.pop("campaign_account_id", None)
            subdomain = args.pop("subdomain", None)

            if context.user_is_super_admin:
                return self.list_campaigns_for_super_admin(context)

            if subdomain:
                campaigns = Campaign.objects.filter(account__subdomain=subdomain,is_deleted=False)

            elif campaign_account_id:
                campaigns = Campaign.objects.filter(account__id=campaign_account_id, is_deleted=False)

            else:
                campaigns = Campaign.objects.filter(Q(is_global=True) | Q(owner__id=context.user_id), is_deleted=False)

            campaign_manager_campaign_ids = CampaignManager.objects.filter(user__id=context.user_id, is_deleted=False).values_list('campaign', flat=True)
            campaign_manager_campaigns = Campaign.objects.filter(id__in=campaign_manager_campaign_ids)
            campaigns = campaigns | campaign_manager_campaigns
            return campaigns.distinct().order_by("-created_at"), None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_campaigns_for_super_admin(self, context: Context):
        try:
            campaigns = Campaign.objects.filter(is_deleted=False)
            return campaigns.order_by("-created_at"), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def add_campaign_manager(self, context: Context, args):
        try:
            email = args.pop("email", None)
            campaign_id = args.pop("campaign_id", None)

            if not campaign_id:
                return None, CustomMassenergizeError("campaign id is required!")

            campaign = Campaign.objects.filter(id=campaign_id).first()

            if not campaign:
                return None, CustomMassenergizeError("campaign with id not found!")

            if not context.user_is_super_admin:
                if context.user_email != campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,campaign__id=campaign_id, is_deleted=False)
                    if not campaign_manager:
                        return None, CustomMassenergizeError("Not authorized to add manager")

            if not email:
                return None, CustomMassenergizeError("email is required!")
            user = UserProfile.objects.filter(email=email).first()
            if not user:
                return None, CustomMassenergizeError("user with email not found!")

            manager, _ = CampaignManager.objects.get_or_create(campaign=campaign, user=user, **args)
            if not _:
                return None, CustomMassenergizeError("campaign manager already exists!")
            return manager, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def remove_campaign_manager(self, context: Context, args):
        try:
            campaign_manager_id = args.pop("campaign_manager_id", None)
            if not campaign_manager_id:
                return None, CustomMassenergizeError("campaign_manager_id is required!")
            campaign_manager = CampaignManager.objects.filter(id=campaign_manager_id).first()
            if not campaign_manager:
                return None, CustomMassenergizeError("manager with id not found!")

            if campaign_manager.is_key_contact:
                return None, CustomMassenergizeError("Cannot delete key contact!")

            campaign_manager.delete()

            return campaign_manager, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)


    def update_campaign_manager(self, context: Context, args):
        try:
            campaign_manager_id = args.pop("campaign_manager_id", None)
            if not campaign_manager_id:
                return None, CustomMassenergizeError("campaign_manager_id is required!")
            campaign_manager = CampaignManager.objects.filter(id=campaign_manager_id)
            if not campaign_manager:
                return None, CustomMassenergizeError("campaign manager with id not found!")

            # check if user is authorized to update
            if not context.user_is_super_admin:
                if context.user_email != campaign_manager.first().campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,campaign__id=campaign_manager.first().campaign.id, is_deleted=False)
                    if not campaign_manager:
                        return None, CustomMassenergizeError("Not authorized to update manager")

            campaign_manager.update(**args)

            return campaign_manager.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def add_campaign_community(self, context: Context, args):
        try:
            community_id = args.pop("community_ids", None)
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required!")
            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("campaign with id not found!")

            if not community_id:
                return None, CustomMassenergizeError("community_ids is required!")

            # check if user is authorized to update
            if not context.user_is_super_admin:
                if context.user_email != campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,campaign__id=campaign_id, is_deleted=False)
                    if not campaign_manager:
                        return None, CustomMassenergizeError("Not authorized to add community")

            campaign_communities = []
            for community_id in community_id:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    campaign_community, exists = CampaignCommunity.objects.get_or_create(campaign=campaign, community=community, is_deleted=False)
                    campaign_communities.append(campaign_community.simple_json())

            CampaignCommunity.objects.filter(campaign=campaign).exclude(id__in=[c["id"] for c in campaign_communities]).update(is_deleted=True)

            # sort by alias or community name
            campaign_communities.sort(key=lambda x: x["alias"] or x["community"]["name"])
            return campaign_communities, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def remove_campaign_community(self, context: Context, args):
        try:
            campaign_community_id = args.pop("id", None)
            if not campaign_community_id:
                return None, CustomMassenergizeError("id is required!")


            campaign_community = CampaignCommunity.objects.filter(id=campaign_community_id).first()
            if not campaign_community:
                return None, CustomMassenergizeError("campaign Community with id not found!")

            if not context.user_is_super_admin:
                if context.user_email != campaign_community.campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,
                                                                      campaign__id=campaign_community.campaign.id,
                                                                      is_deleted=False)
                    if not campaign_manager:
                        return None, CustomMassenergizeError("Not authorized to remove community")

            campaign_community.delete()
            return campaign_community, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_campaign_community(self, context: Context, args):
        try:
            extra_links = args.pop("extra_links", [])
            campaign_community_id = args.pop("campaign_community_id", None)
            if not campaign_community_id:
                return None, CustomMassenergizeError("campaign_community_id is required!")
            campaign_community = CampaignCommunity.objects.filter(id=campaign_community_id)
            if not campaign_community:
                return None, CustomMassenergizeError("campaign community with id not found!")
            if extra_links:
                info = campaign_community.first().info or {}
                args["info"] = {**info, "extra_links": extra_links}

            # check if user is authorized to update
            if not context.user_is_super_admin:
                if context.user_email != campaign_community.first().campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,campaign__id=campaign_community.first().campaign.id, is_deleted=False)
                    if not campaign_manager:
                        return None, CustomMassenergizeError("Not authorized to update community")

            campaign_community.update(**args)

            return campaign_community.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def add_campaign_technology(self, context: Context, args):
        try:
            technology_ids = args.pop("technology_ids", None)
            campaign_id = args.pop("campaign_id", None)

            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required!")
            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("campaign with id not found!")

            if not technology_ids:
                return None, CustomMassenergizeError("technology_ids is required!")

            # check if user is authorized to update
            if not context.user_is_super_admin:
                if context.user_email != campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,campaign__id=campaign_id, is_deleted=False)
                    if not campaign_manager:
                        return None, CustomMassenergizeError("Not authorized to add technology")


            for technology_id in technology_ids:
                technology = Technology.objects.filter(id=technology_id).first()
                if not technology:
                    return None, CustomMassenergizeError("technology with id not found!")

                CampaignTechnology.objects.get_or_create(campaign=campaign, technology=technology, is_deleted=False)

            return CampaignTechnology.objects.filter(campaign=campaign, is_deleted=False), None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_campaign_technology(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("id", None)
            if not campaign_technology_id:
                return None, CustomMassenergizeError("id is required!")

            campaign_technology = CampaignTechnology.objects.filter(id=campaign_technology_id)
            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign Technology with id not found!")

            campaign_technology.update(**args)

            return campaign_technology.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def remove_campaign_technology(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("id", None)
            if not campaign_technology_id:
                return None, CustomMassenergizeError("id is required!")

            campaign_technology = CampaignTechnology.objects.filter(id=campaign_technology_id
            ).first()
            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign Technology with id not found!")

            if not context.user_is_super_admin:
                if context.user_email != campaign_technology.campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,campaign__id=campaign_technology.campaign.id, is_deleted=False)
                    if not campaign_manager:
                        return None, CustomMassenergizeError("Not authorized to remove technology")

            campaign_technology.is_deleted = True
            campaign_technology.save()

            return campaign_technology, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def create_campaign_technology_testimonial(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            community_id = args.pop("community_id", None)
            image = args.pop("image", None)
            user_id = args.pop("user_id", context.user_id)
            name = args.pop("name", None)
            email = args.pop("email", None)
            user = None

            if not campaign_technology_id:
                return None, CustomMassenergizeError("Campaign Technology ID is required !")

            campaign_technology = CampaignTechnology.objects.filter(id=campaign_technology_id).first()
            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign Technology with id not found!")

            args["campaign_technology"] = campaign_technology

            if name and email:
                user, _ = UserProfile.objects.get_or_create(email=email, full_name=name)
                if _:
                    user.user_info = {"user_type": LOOSED_USER}
                    user.save()
            else:
                if not user_id:
                    return None, CustomMassenergizeError("User ID is required !")

                user = UserProfile.objects.filter(id=user_id).first()
                if not user:
                    return None, CustomMassenergizeError("User with id not found!")


            if community_id:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    args["community"] = community

            if not user:
                return None, CustomMassenergizeError("User not found!")

            testimonial = Testimonial()
            testimonial.title = args.get("title", None)
            testimonial.body = args.get("body", None)
            testimonial.user = user
            testimonial.image = create_media_file(image, f"ImageFor {testimonial.title} Campaign")
            testimonial.community = community
            testimonial.is_published = args.get("is_published", False)
            testimonial.save()

            campaign_testimonial, _ = CampaignTechnologyTestimonial.objects.get_or_create(campaign_technology=campaign_technology, testimonial=testimonial, is_deleted=False)

            return campaign_testimonial, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_campaign_technology_testimonial(self, context: Context, args):
        try:
            campaign_technology_testimonial_id = args.pop("id", None)
            community_id = args.pop("community_id", None)
            image = args.pop("image", None)

            if not campaign_technology_testimonial_id:
                return None, CustomMassenergizeError("id is required !")

            campaign_technology_testimonial = CampaignTechnologyTestimonial.objects.get(id=campaign_technology_testimonial_id)

            is_featured = args.pop("is_featured", campaign_technology_testimonial.is_featured)

            if not campaign_technology_testimonial:
                return None, CustomMassenergizeError("Campaign Technology testimonial with id not found!")

            testimonial = campaign_technology_testimonial.testimonial

            if image:
                img =  create_media_file(image, f"ImageFor {testimonial.title} Campaign")
                testimonial.image = img


            if community_id:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    testimonial.community = community

            testimonial.title = args.get("title", testimonial.title)
            testimonial.body = args.get("body", testimonial.body)
            testimonial.is_published = args.get("is_published", testimonial.is_published)
            testimonial.is_approved = args.get("is_published", testimonial.is_published)
            testimonial.save()

            campaign_technology_testimonial.is_featured = is_featured if testimonial.is_published else False
            campaign_technology_testimonial.save()

            return campaign_technology_testimonial, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def create_campaign_technology_comment(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            community_id: str = args.pop("community_id", None)
            user_id: str = args.pop("user_id", context.user_id)
            comment_text: str = args.get("text", None)
            is_from_admin_site = args.pop("is_from_admin_site", False)

            # check for swear words in comment text
            if contains_profane_words(comment_text):
                return None, CustomMassenergizeError("Comment contains inappropriate language.")

            if campaign_technology_id:
                campaign_technology = CampaignTechnology.objects.get(id=campaign_technology_id)
                if campaign_technology:
                    args["campaign_technology"] = campaign_technology

            if not user_id:
                return None, CustomMassenergizeError("user_id is required !")
            user = UserProfile.objects.filter(id=user_id).first()
            if not user:
                return None, CustomMassenergizeError("user with id not found!")
            args["user"] = user

            if community_id:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    args["community"] = community

            comment, _ = Comment.objects.get_or_create(**args)

            if is_from_admin_site:
                return comment, None

            latest_comments = Comment.objects.filter(campaign_technology__id=campaign_technology_id, is_deleted=False).order_by("-created_at")
            return latest_comments[:20], None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_campaign_technology_comment(self, context: Context, args):
        try:
            comment_id = args.pop("id", None)
            if not comment_id:
                return None, CustomMassenergizeError("id is required !")

            comment = Comment.objects.filter(id=comment_id)
            if not comment:
                return None, CustomMassenergizeError("Comment with id not found!")

            comment.update(**args)

            return comment.first(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)


    def list_campaign_technology_comments(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required!")
            comments = Comment.objects.filter(campaign_technology__campaign__id=campaign_id, is_deleted=False, campaign_technology__is_deleted=False).order_by("-created_at")

            return comments, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_campaign_technology_testimonials(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required!")
            testimonials = CampaignTechnologyTestimonial.objects.filter(campaign_technology__campaign__id=campaign_id, is_deleted=False, campaign_technology__is_deleted=False)

            return testimonials.order_by("-created_at"), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def delete_campaign_technology_testimonial(self, context: Context, args):
        try:
            campaign_technology_testimonial_id = args.pop("id", None)
            if not campaign_technology_testimonial_id:
                return None, CustomMassenergizeError("id is required !")

            campaign_technology_testimonial = CampaignTechnologyTestimonial.objects.filter(id= campaign_technology_testimonial_id).first()
            if not campaign_technology_testimonial:
                return None, CustomMassenergizeError("Campaign Technology testimonial with id not found!")

            if not context.user_is_super_admin:
                if context.user_email != campaign_technology_testimonial.campaign_technology.campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,campaign__id=campaign_technology_testimonial.campaign_technology.campaign.id, is_deleted=False)
                    if not campaign_manager:
                        return None, CustomMassenergizeError("Not authorized to remove testimonial")

            campaign_technology_testimonial.is_deleted = True
            campaign_technology_testimonial.save()

            return campaign_technology_testimonial, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_campaign_technologies(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required!")
            technologies = CampaignTechnology.objects.filter(campaign__id=campaign_id, is_deleted=False)

            return technologies, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_campaign_communities(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required!")
            communities = CampaignCommunity.objects.filter(campaign__id=campaign_id, is_deleted=False)
            return communities, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_campaign_managers(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required!")
            managers = CampaignManager.objects.filter(campaign__id=campaign_id, is_deleted=False)

            return managers, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def add_campaign_partners(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            partner_ids = args.pop("partner_ids", None)

            created_list = []

            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required!")

            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("campaign with id not found!")

            if not partner_ids:
                return None, CustomMassenergizeError("partner_ids is required!")

            for partner_id in partner_ids:
                partner = Partner.objects.filter(id=partner_id).first()
                if partner:
                    campaign_partner, _ = CampaignPartner.objects.get_or_create(
                        campaign=campaign, partner=partner
                    )
                    created_list.append(campaign_partner.to_json())

            return created_list, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def remove_campaign_partners(self, context: Context, args):
        try:
            campaign_partner_id = args.pop("campaign_partner_id", None)
            if not campaign_partner_id:
                return None, CustomMassenergizeError("campaign_partner_id is required!")

            campaign_partner = CampaignPartner.objects.filter(
                id=campaign_partner_id
            ).first()
            if not campaign_partner:
                return None, CustomMassenergizeError("Campaign Partner with id not found!")

            campaign_partner.is_deleted = True
            campaign_partner.save()

            return campaign_partner, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_campaign_partners(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required!")
            partners = CampaignPartner.objects.filter(
                campaign__id=campaign_id, is_deleted=False
            )

            return partners, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def add_campaign_technology_event(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            event_ids = args.pop("event_ids", None)

            created_list = []

            if not campaign_technology_id:
                return None, CustomMassenergizeError("campaign_technology_id is required!")
            campaign_tech = CampaignTechnology.objects.filter(id=campaign_technology_id).first()
            if not campaign_tech:
                return None, CustomMassenergizeError("campaignTechnology with id not found!")

            if not event_ids:
                return None, CustomMassenergizeError("event_ids is required!")

            if not context.user_is_super_admin:
                if context.user_email != campaign_tech.campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,campaign__id=campaign_tech.campaign.id, is_deleted=False)
                    if not campaign_manager:
                        return None, CustomMassenergizeError("Not authorized to add event")

            for event_id in event_ids:
                event = Event.objects.filter(id=event_id).first()
                if event:
                    campaign_event, _ = CampaignTechnologyEvent.objects.get_or_create(campaign_technology=campaign_tech, event=event, is_deleted=False)
                    created_list.append(campaign_event.simple_json())

            return created_list, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def generate_campaign_link(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            utm_source = args.pop("utm_source", None)
            utm_medium = args.pop("utm_medium", None)
            utm_campaign = args.pop("utm_campaign", None)
            url = args.pop("url", None)
            email = args.pop("email", None)

            # remove trailing slash in url if it exists
            if url and url[-1] == "/":
                url = url[:-1]

            if not campaign_id:
                return None, CustomMassenergizeError("Campaign id not found!")

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

            generated_link = f"{url}?utm_source={utm_source}&utm_medium={utm_medium}&link_id={campaign_link.id}"
            return {"link": generated_link}, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def campaign_link_visits_count(self, context, args):
        try:
            campaign_link_id = args.pop("campaign_link_id", None)
            if not campaign_link_id:
                return None, CustomMassenergizeError("campaign_link_id is required!")

            campaign_link = CampaignLink.objects.filter(id=campaign_link_id).first()
            if campaign_link:
                campaign_link.increase_count()

            return campaign_link, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def add_campaign_follower(self, context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            community_id: str = args.pop("community_id", None)

            email = args.pop("email", None)
            is_other = args.pop("is_other", False)

            if not campaign_id:
                return None, CustomMassenergizeError("Campaign id not found!")

            if not community_id and not is_other:
                return None, CustomMassenergizeError("Please select a community!")

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

            follower, _ = CampaignFollow.objects.get_or_create(campaign=campaign, **args)

            return follower, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def add_campaign_technology_follower(self, context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            community_id: str = args.pop("community_id", None)

            email = args.pop("email", None)
            is_other = args.pop("is_other", False)

            if not campaign_technology_id:
                return None, CustomMassenergizeError("Campaign technology id not found!")

            campaign_technology = CampaignTechnology.objects.filter(id=campaign_technology_id).first()
            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign technology with id not found!")

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

            follower, _ = CampaignTechnologyLike.objects.get_or_create(campaign_technology=campaign_technology, **args)

            return follower, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)



    def add_campaign_technology_like(self, context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            if not campaign_technology_id:
                return None, CustomMassenergizeError("Campaign technology id not found!")

            campaign_technology = CampaignTechnology.objects.filter( id=campaign_technology_id).first()
            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign technology with id not found!")
            like, _ = CampaignTechnologyLike.objects.get_or_create(campaign_technology=campaign_technology)
            # lock transaction
            with transaction.atomic():
                like.increase_count()

            campaign_tech = get_campaign_technology_details({"campaign_technology_id":campaign_technology_id})

            return campaign_tech, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def add_campaign_technology_view(self, context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            url = args.pop("url", None)
            if not campaign_technology_id:
                return None, CustomMassenergizeError("campaign_technology_id not found!")

            campaign_technology = CampaignTechnology.objects.filter(id=campaign_technology_id).first()
            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign technology with id not found!")

            link_id = url.split("&link_id=")
            link_id = link_id[1] if len(link_id) > 1 else None

            if link_id:
                campaign_link = CampaignLink.objects.filter(id=link_id).first()
                if campaign_link:
                    with transaction.atomic():
                        campaign_link.increase_count()

            view, _ = CampaignTechnologyView.objects.get_or_create(campaign_technology=campaign_technology)
            # lock transaction
            with transaction.atomic():
                view.increase_count()
            return view, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_campaign_technology_event(self, context: Context, args):
        try:
            campaign_technology_id = args.pop("campaign_technology_id", None)
            if not campaign_technology_id:
                return None, CustomMassenergizeError("campaign_technology_id not found!")
            events = CampaignTechnologyEvent.objects.filter(campaign_technology__id=campaign_technology_id, is_deleted=False)

            return events, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def get_campaign_analytics(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id not found!")
            campaign = None
            try:
                uuid_id = UUID(campaign_id, version=4)
                campaign = Campaign.objects.filter(id=uuid_id, is_deleted=False).first()
            except ValueError:
                campaign = Campaign.objects.filter(slug=campaign_id, is_deleted=False).first()

            if not campaign:
                return None, CustomMassenergizeError("Campaign with id not found!")

            # check if user is authorized to view analytics add user not a manager
            if not context.user_is_super_admin:
                if not context.user_email == campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id, campaign__id=campaign_id)
                    if not campaign_manager:
                        return None, NotAuthorizedError()


            stats = generate_analytics_data(campaign.id)
            stats["campaign"] = {
                "title": campaign.title,
                "image": campaign.image.file.url if campaign.image else None,
                "tagline": campaign.tagline,
                "start_date": campaign.start_date,
                "end_date": campaign.end_date,
                "id": str(campaign.id),
                "slug": campaign.slug,
                "is_published":campaign.is_published
            }
            return stats, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)


    def add_campaign_like(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("Campaign id not found!")

            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign with id not found!")

            like = CampaignLike.objects.create(campaign=campaign, **args)

            return like, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def transfer_ownership(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            new_owner_id = args.pop("user_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("Campaign id not found!")

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
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def get_campaign_technology_info(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_technology_id = args.get("campaign_technology_id", None)
            campaign_technology: CampaignTechnology = CampaignTechnology.objects.filter(id=campaign_technology_id).first()

            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign Technology not found")

            return campaign_technology, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def get_campaign_technology_testimonial(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_technology_testimonial_id = args.get("id", None)
            campaign_technology_testimonial =CampaignTechnologyTestimonial.objects.filter(id=campaign_technology_testimonial_id).first()

            if not campaign_technology_testimonial:
                return None, CustomMassenergizeError("Campaign Technology Testimonial not found")

            return campaign_technology_testimonial, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def create_campaign_config(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id not provided")

            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign not found")

            config = CampaignConfiguration.objects.create(campaign=campaign, **args)
            return config, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_campaign_config(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_config_id = args.pop("id", None)
            if not campaign_config_id:
                return None, CustomMassenergizeError("campaign_config_id not provided")

            campaign_config = CampaignConfiguration.objects.filter(id=campaign_config_id).first()
            if not campaign_config:
                return None, CustomMassenergizeError("Campaign Config not found")

            campaign_config.update(**args)
            return campaign_config, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def get_campaign_config(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign_config_id = args.get("id", None)
            if not campaign_config_id:
                return None, CustomMassenergizeError("campaign_config_id not provided")

            campaign_config = CampaignConfiguration.objects.filter(id=campaign_config_id).first()
            if not campaign_config:
                return None, CustomMassenergizeError("Campaign Config not found")

            return campaign_config, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def create_campaign_navigation(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        campaign_id = args.pop("campaign_id", None)

        if not campaign_id:
            return None, CustomMassenergizeError("Campaign id not provided")

        nav = generate_campaign_navigation(campaign_id)
        return nav, None

    def create_campaign_from_template(self, context: Context, args: dict):
        try:
            account_id = args.pop("campaign_account_id", None)
            community_ids = args.pop("community_ids", [])
            title = args.pop("title", None)
            template_key = args.pop("template_key", None)

            user = get_user_from_context(context)

            if not user:
                return None, CustomMassenergizeError("User not found")

            if template_key == CAMPAIGN_TEMPLATE_KEYS.get("MULTI_TECHNOLOGY_CAMPAIGN"):
                if not community_ids:
                    return None, CustomMassenergizeError("Community ids not provided")

            if not account_id:
                return None, CustomMassenergizeError("Account id not provided")

            if not title:
                return None, CustomMassenergizeError("Title not provided")

            account = CampaignAccount.objects.filter(id=account_id).first()

            new_campaign = Campaign()
            new_campaign.title = title
            new_campaign.account = account
            new_campaign.is_global = False
            new_campaign.is_template = False
            new_campaign.owner = user
            new_campaign.template_key = template_key
            new_campaign.save()

            for community_id in community_ids:
                community = Community.objects.filter(id=community_id).first()
                if community:
                    CampaignCommunity.objects.create(campaign=new_campaign, community=community)

            copy_campaign_data(new_campaign)

            return new_campaign, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def track_activity(self, context: Context, args: dict):
        try:
            campaign_id = args.pop("campaign_id", None)

            if not campaign_id:
                return None, CustomMassenergizeError("Campaign ID not provided")
            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign with  ID not found")

            activity = CampaignActivityTracking.objects.create(campaign=campaign, **args)

            return activity, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)


    def add_campaign_view(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            url = args.pop("url", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id not found!")

            campaign = None
            try:
                uuid_id = UUID(campaign_id, version=4)
                campaign = Campaign.objects.filter(id=uuid_id, is_deleted=False).first()
            except ValueError:
                campaign = Campaign.objects.filter(slug=campaign_id, is_deleted=False).first()
            if not campaign:
                return None, CustomMassenergizeError("Campaign with id not found!")
            if url:
                link_id = url.split("&link_id=")
                link_id = link_id[1] if len(link_id) > 1 else None

                if link_id:
                    campaign_link = CampaignLink.objects.filter(id=link_id).first()
                    if campaign_link:
                        with transaction.atomic():
                            campaign_link.increase_count()

            view, _ = CampaignView.objects.get_or_create(campaign=campaign, is_deleted=False)
            # lock transaction
            with transaction.atomic():
                view.increase_count()
            return view, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)


    def delete_campaign_technology_comment(self, context: Context, args):
        try:
            comment_id = args.pop("id", None)
            user_id = args.pop("user_id", context.user_id)
            if not comment_id:
                return None, CustomMassenergizeError("id is required !")

            comment = Comment.objects.filter(id=comment_id).first()
            if not comment:
                return None, CustomMassenergizeError("Comment with id not found!")
            if str(comment.user.id) != user_id and not context.user_is_admin():
                return None, CustomMassenergizeError("You are not authorized to delete this comment!")
            comment.is_deleted = True
            comment.save()

            comment = Comment.objects.filter(campaign_technology__id=comment.campaign_technology.id, is_deleted=False).order_by("-created_at")

            return comment[:20], None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)



    def create_campaign_technology(self, context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            image = args.pop("image", None)
            campaign_account_id = args.pop("campaign_account_id", None)

            user = get_user_from_context(context)

            if not campaign_id:
                return None, CustomMassenergizeError("Campaign ID is required !")

            campaign = Campaign.objects.filter(id=campaign_id).first()
            if not campaign:
                return None, CustomMassenergizeError("campaign with id not found!")


            if not campaign_account_id:
                 return None, CustomMassenergizeError("campaign_account_id is required !")
            account = CampaignAccount.objects.get(id=campaign_account_id)
            if not account:
                return None, CustomMassenergizeError("campaign_account with id not found!")

            if not context.user_is_super_admin:
                if not context.user_email == campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id, campaign__id=campaign_id)
                    if not campaign_manager:
                        return None, NotAuthorizedError()


            if image:
                name = f"ImageFor {campaign.title} technology"
                media = Media.objects.create(name=name, file=image)
                args["image"] = media

            technology = Technology()
            technology.name = args.pop("name", None)
            technology.description = args.pop("description", None)
            technology.image = args.pop("image", None)
            technology.summary = args.pop("summary", None)
            technology.campaign_account = account
            technology.help_link = args.pop("help_link", None)
            technology.user = user
            technology.save()

            campaign_technology = CampaignTechnology.objects.create(campaign=campaign, technology=technology)

            return campaign_technology, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)



    def list_campaign_communities_events(self, context: Context, args):
        try:
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required!")
            communities = CampaignCommunity.objects.filter(campaign__id=campaign_id, is_deleted=False)
            events = []
            for community in communities:
                events.extend(Event.objects.filter(community__id=community.community.id, is_deleted=False, is_published=True))
            to_return = []
            for event in events:
                obj = {
                    "id": event.id,
                    "name": event.name,
                    "community":{
                        "id": event.community.id,
                        "name": event.community.name,
                        "alias": communities.filter(campaign__id=campaign_id, community__id=event.community.id).first().alias
                    }
                }
                to_return.append(obj)


            return to_return, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))



    def list_campaign_communities_testimonials(self, context: Context, args):
        try:
            campaign_id = args.get("campaign_id")

            if not campaign_id:
                raise CustomMassenergizeError("campaign_id is required!")

            campaign_communities = CampaignCommunity.objects.filter(campaign__id=campaign_id, is_deleted=False)

            existing_testimonials = CampaignTechnologyTestimonial.objects.filter(Q(campaign_technology__campaign__id=campaign_id, is_deleted=False)).values_list('testimonial_id', flat=True)

            testimonials = Testimonial.objects.filter(community__in=campaign_communities.values_list('community_id', flat=True),
                is_published=True,
                is_deleted=False
            ).exclude(id__in=existing_testimonials)

            to_return = []

            for testimonial in testimonials:
                obj = {
                    "id": testimonial.id,
                    "title": testimonial.title,
                    "community": {
                        "id": testimonial.community.id,
                        "name": testimonial.community.name,
                        "alias": campaign_communities.filter(campaign__id=campaign_id, community__id=testimonial.community.id).first().alias
                    }
                }
                to_return.append(obj)

            return to_return, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))



    def list_campaign_communities_vendors(self, context: Context, args):
        try:
            vendors = Vendor.objects.filter(is_deleted=False, is_published=True)
            return vendors, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)


    def add_campaign_technology_testimonial(self, context:Context, args:dict):
        try:
            technology_id = args.pop("technology_id", None)
            campaign_id = args.pop("campaign_id", None)
            testimonial_ids = args.pop("testimonial_ids", [])
            if not campaign_id and not technology_id:
                return None, CustomMassenergizeError("campaign_id and technology_id are required !")

            campaign_technology = CampaignTechnology.objects.filter(campaign__id=campaign_id, technology__id=technology_id, is_deleted=False).first()
            if not campaign_technology:
                return None, CustomMassenergizeError("Campaign Technology  not found!")

            if not testimonial_ids:
                return None, CustomMassenergizeError("testimonial_ids is required !")

            # check if user is authorized to add testimonial
            if not context.user_is_super_admin:
                if context.user_email != campaign_technology.campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id, campaign__id=campaign_id, is_deleted=False)
                    if not campaign_manager:
                        return None, NotAuthorizedError()

            testimonials = []
            for testimonial_id in testimonial_ids:
                testimonial = Testimonial.objects.get(pk=testimonial_id, is_deleted=False)
                tech_testimonial, exists = CampaignTechnologyTestimonial.objects.get_or_create(campaign_technology=campaign_technology, testimonial=testimonial, is_deleted=False)
                tech_testimonial.is_featured = True
                tech_testimonial.is_imported = True
                tech_testimonial.save()

                testimonials.append(tech_testimonial.simple_json())

            return testimonials, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)


    def remove_campaign_technology_event(self, context:Context, args:dict):
        try:
            tech_event_id = args.pop("id", None)
            if not tech_event_id:
                return None, CustomMassenergizeError("id is required !")

            campaign_technology_event = CampaignTechnologyEvent.objects.filter(pk=tech_event_id).first()
            if not campaign_technology_event:
                return None, CustomMassenergizeError("Campaign Technology Event not found!")

            if not context.user_is_super_admin:
                if context.user_email != campaign_technology_event.campaign_technology.campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,campaign__id=campaign_technology_event.campaign_technology.campaign.id, is_deleted=False)
                    if not campaign_manager:
                        return None, CustomMassenergizeError("Not authorized to remove event")

            campaign_technology_event.delete()

            return campaign_technology_event, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)


    def update_campaign_key_contact(self, context:Context, args:dict):
        try:
            manager_id = args.pop("manager_id", None)
            campaign_id = args.pop("campaign_id", None)
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required !")

            campaign = Campaign.objects.get(id=campaign_id, is_deleted=False)
            if not campaign:
                return None, CustomMassenergizeError("Campaign with id not found!")

            if not manager_id:
                return None, CustomMassenergizeError("manager_id is required !")

            if not context.user_is_super_admin:
                if not context.user_email == campaign.owner.email:
                    campaign_manager = CampaignManager.objects.filter(user__id=context.user_id,campaign__id=campaign_id)
                    if not campaign_manager:
                        return None, NotAuthorizedError()


            campaign_managers = CampaignManager.objects.filter(campaign__id=campaign_id, is_deleted=False)
            campaign_managers.update(is_key_contact=False)
            # assign the new key contact
            campaign_manager = campaign_managers.get(pk=manager_id, is_deleted=False)
            if not campaign_manager:
                return None, CustomMassenergizeError("Campaign Manager not found!")
            campaign_manager.is_key_contact = True
            campaign_manager.save()


            return campaign_managers.order_by("-created_at"), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)


    def delete_call_to_action(self, context: Context, args: dict):
        try:
            cta_id = args.pop("id", None)
            if not cta_id:
                return None, CustomMassenergizeError("id is required !")

            cta = CallToAction.objects.filter(pk=cta_id).first()
            if not cta:
                return None, CustomMassenergizeError("Call to action not found!")

            cta.delete()
            return cta, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
        
    def add_campaign_media(self, context: Context, args: dict):
        try:
            campaign_id = args.pop("campaign_id", None)
            media = args.pop("media", None)
            order = args.pop("order", 1)
            
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required !")
            
            if not media:
                return None, CustomMassenergizeError("media_id is required !")

            campaign = Campaign.objects.get(pk=campaign_id, is_deleted=False)
            
            if not campaign:
                return None, CustomMassenergizeError("Campaign not found!")

            media = create_media_file(media, f"section-{campaign.title}-media-{order}")

            campaign_media, _ = CampaignMedia.objects.get_or_create(campaign=campaign, media=media, order=order)

            return campaign_media, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
        
    def delete_campaign_media(self, context: Context, args: dict):
        try:
            media_id = args.pop("id", None)
            if not media_id:
                return None, CustomMassenergizeError("id is required !")

            media = CampaignMedia.objects.filter(pk=media_id).first()
            if not media:
                return None, CustomMassenergizeError("Campaign Media not found!")

            media.delete()
            return media, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
        
    def update_campaign_media(self, context: Context, args: dict):
        try:
            campaign_media_id = args.pop("id", None)
            order = args.pop("order", None)
            media = args.pop("media", None)
            
            if not campaign_media_id:
                return None, CustomMassenergizeError("id is required !")

            campaign_media = CampaignMedia.objects.filter(pk=campaign_media_id).first()
            if not campaign_media:
                return None, CustomMassenergizeError("Campaign Media not found!")
            
            if media:
                media = create_media_file(media, f"section-{campaign_media.campaign.title}-media-{order}")
                if media:
                    campaign_media.media = media
                    
            campaign_media.order = order
            campaign_media.save()
            return campaign_media, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
        
        
    def campaign_contact_us(self, context: Context, args: dict):
        try:
            campaign_id = args.pop("campaign_id", None)
            email = args.pop("email", None)
            message = args.pop("message", None)
            full_name = args.pop("full_name", None)
            phone_number = args.pop("phone_number", None)
            language = args.pop("language", None)
            community_id = args.pop("community_id", None)
            other = args.pop("other", None)
            
            community = None
            
            if not campaign_id:
                return None, CustomMassenergizeError("campaign_id is required !")
            
            if not email:
                return None, CustomMassenergizeError("email is required !")
            
            campaign = None
            try:
                uuid_id = UUID(campaign_id, version=4)
                campaign = Campaign.objects.filter(id=uuid_id, is_deleted=False).first()
            except ValueError:
                campaign = Campaign.objects.filter(slug=campaign_id, is_deleted=False).first()
            
            if not campaign:
                return None, CustomMassenergizeError("Campaign with id does not exist")

        
            if community_id:
                community = Community.objects.get(pk=community_id, is_deleted=False)
            else:
                community, _ = Community.objects.get_or_create(name="Other")
                
            campaign_contact = CampaignContact(
                campaign=campaign,
                email=email,
                message=message,
                full_name=full_name,
                phone_number=phone_number,
                language=language,
                community=community
            )
            if other:
                campaign_contact.info = other
            campaign_contact.save()
                
            #  send email to user
            send_massenergize_email_with_attachments(
                THANK_YOU_FOR_GETTING_IN_TOUCH_TEMPLATE,
                {
                    "campaign_name": campaign.title,
                    "campaign_url": f"{CAMPAIGN_URL_ROOT}/campaign/{campaign.slug}",
                    "year": datetime.now().year,
                },
                [email],
                None,
                None,
            )
            
            # send email to admin
            admin = campaign.campaign_manager.filter(is_key_contact=True).first().user
            send_massenergize_email_with_attachments(
                CAMPAIGN_CONTACT_MESSAGE_TEMPLATE,
                {
                    "admin_name": admin.full_name if admin else "Admin",
                    "campaign_name": campaign.title,
                    "full_name": full_name,
                    "email": email,
                    "phone_number": phone_number,
                    "language":language,
                    "year": datetime.now().year,
                },
                
                [admin.email],
                None,
                None,
            )
            
            return {"message": "Email sent successfully"}, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
