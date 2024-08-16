from apps__campaigns.models import Campaign
from database.models import CampaignSupportedLanguage, SupportedLanguage, CommunitySupportedLanguage, Community
from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.activity_logger import log
from typing import Tuple
from django.db import IntegrityError
from _main_.utils.constants import DEFAULT_SOURCE_LANGUAGE_CODE, INVALID_LANGUAGE_CODE_ERR_MSG, INVALID_COMMUNITY_LANGUAGE_CODE_ERR_MSG

COMMUNITY_NOT_FOUND_ERR_MSG = "Community with ID: {} not found"


class SupportedLanguageStore:
    def __init__ (self):
        self.name = "Supported Language Store/DB"

    def get_supported_language_info (self, args) -> Tuple[ dict or None, any ]:
        try:
            language_code = args.get('language_code', None)

            if not language_code:
                return None, CustomMassenergizeError(f"{INVALID_LANGUAGE_CODE_ERR_MSG}: {language_code}")

            language = SupportedLanguage.objects.filter(code = language_code).first()

            return language, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

    def list_supported_languages (self, context, args) -> Tuple[ list or None, any ]:
        try:
            languages = SupportedLanguage.objects.all()
            return languages, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

    def create_supported_language (self, args) -> Tuple[ SupportedLanguage or None, None or CustomMassenergizeError ]:
        try:
            language = SupportedLanguage.objects.create(code = args.get('language_code', None), name = args.get('name', None))
            return language, None

        except IntegrityError as e:
            log.exception(e)
            return None, CustomMassenergizeError(
                f"A Supported Language with code: '{args.get('language_code', None)}' already exists")

        except Exception as e:
            log(e)
            return None, CustomMassenergizeError(str(e))

    def disable_supported_language (self, context, language_code) -> Tuple[ SupportedLanguage or None, any ]:
        try:
            language = SupportedLanguage.objects.filter(code = language_code).first()

            if not language:
                return None, CustomMassenergizeError(f"{INVALID_LANGUAGE_CODE_ERR_MSG}: {language_code}")

            language.is_disabled = True
            language.save()

            return language, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

    def enable_supported_language (self, context, language_code) -> Tuple[ SupportedLanguage or None, any ]:
        try:
            language = SupportedLanguage.objects.filter(code = language_code).first()

            if not language:
                return None, CustomMassenergizeError(f"{INVALID_LANGUAGE_CODE_ERR_MSG}: {language_code}")

            language.is_disabled = False
            language.save()

            return language, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

    def update_campaign_supported_language(self, context,  args):
        try:
            campaign_id = args.get('campaign_id', None)
            supported_languages_dict = args.get('supported_languages', None)

            if not campaign_id:
                return None, CustomMassenergizeError("Please provide a campaign_id")

            campaign = Campaign.objects.get(pk=campaign_id)

            if not campaign:
                return None, CustomMassenergizeError("Campaign not found")

            if not supported_languages_dict:
                return None, CustomMassenergizeError("Please provide supported_languages")

            supported_languages_codes = list(supported_languages_dict.keys())

            supported_languages = SupportedLanguage.objects.filter(code__in=supported_languages_codes)

            campaign_supported_languages = campaign.supported_languages.all()

            active_codes =[]
            disabled_codes = []

            new_campaign_supported_languages = []

            for key, value in supported_languages_dict.items():
                lang = campaign_supported_languages.filter(language__code=key).first()
                if lang:
                    if value:
                        active_codes.append(key)
                    else:
                        disabled_codes.append(key)
                else:
                    new_campaign_supported_language = CampaignSupportedLanguage(
                        campaign=campaign,
                        language=supported_languages.filter(code=key).first(),
                        is_active=value
                    )
                    new_campaign_supported_languages.append(new_campaign_supported_language)

            if len(new_campaign_supported_languages) > 0:
                CampaignSupportedLanguage.objects.bulk_create(new_campaign_supported_languages)

            campaign_supported_languages_to_activate = campaign_supported_languages.filter(language__code__in=active_codes)
            campaign_supported_languages_to_activate.update(is_active=True)

            campaign_supported_languages_to_disable = campaign_supported_languages.filter(language__code__in=disabled_codes)
            campaign_supported_languages_to_disable.update(is_active=False)

            campaign_supported_languages = campaign.supported_languages.all()

            return campaign_supported_languages, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

    def list_campaign_supported_languages(self, context, args):
        try:
            campaign_id = args.get('campaign_id', None)

            if not campaign_id:
                return None, CustomMassenergizeError("Please provide a campaign_id")

            campaign = Campaign.objects.filter(pk=campaign_id).first()

            if not campaign:
                return None, CustomMassenergizeError("Campaign not found")

            campaign_supported_languages = campaign.supported_languages.all()
            all_supported_languages = SupportedLanguage.objects.all()

            campaign_supported_languages_codes = [lang.language.code for lang in campaign_supported_languages]
            all_supported_languages_codes = [lang.code for lang in all_supported_languages]

            supported_languages_codes = list(set(all_supported_languages_codes) - set(campaign_supported_languages_codes))
            supported_languages = all_supported_languages.filter(code__in=supported_languages_codes)

            new_campaign_supported_languages = []
            for lang in supported_languages:
                new_campaign_supported_language = CampaignSupportedLanguage(
                    campaign=campaign,
                    language=lang,
                    is_active=False if lang.code != DEFAULT_SOURCE_LANGUAGE_CODE else True
                )
                new_campaign_supported_languages.append(new_campaign_supported_language)

            if len(new_campaign_supported_languages) > 0:
                CampaignSupportedLanguage.objects.bulk_create(new_campaign_supported_languages)

            return campaign.supported_languages.all(), None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))


    def get_community_supported_languages(self, community_id) -> Tuple[ list or None, any ]:
        try:
            community = Community.objects.get(id=community_id)

            if community is None:
                log.error(COMMUNITY_NOT_FOUND_ERR_MSG.format(community_id))
                return None, COMMUNITY_NOT_FOUND_ERR_MSG.format(community_id)

            languages = CommunitySupportedLanguage.objects.filter(community = community_id)
            return languages, None
        except Exception as e:
            print(e)
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

    def add_community_supported_language(self, community_id, language_code) -> Tuple[ CommunitySupportedLanguage or None, any ]:
        try:
            language = SupportedLanguage.objects.filter(code = language_code).first()
            if not language:
                return None, CustomMassenergizeError(f"{INVALID_LANGUAGE_CODE_ERR_MSG}: {language_code}")

            community_language = CommunitySupportedLanguage.objects.create(community = community_id, language = language)
            return community_language, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

    def remove_community_supported_language(self, community_id, language_code) -> Tuple[ bool, any ]:
        try:
            language = SupportedLanguage.objects.filter(code = language_code).first()
            if not language:
                return False, CustomMassenergizeError(f"{INVALID_LANGUAGE_CODE_ERR_MSG}: {language_code}")

            community_language = CommunitySupportedLanguage.objects.filter(community = community_id, language = language).first()
            if not community_language:
                return False, CustomMassenergizeError(f"{INVALID_COMMUNITY_LANGUAGE_CODE_ERR_MSG}: {language_code}")

            community_language.delete()
            return True, None
        except Exception as e:
            log.exception(e)
            return False, CustomMassenergizeError(str(e))


    def update_community_supported_language(self, community_id, language_code, is_enabled) -> Tuple[ bool, any ]:
        try:
            language = SupportedLanguage.objects.filter(code = language_code).first()

            if not language:
                return False, CustomMassenergizeError(f"{INVALID_LANGUAGE_CODE_ERR_MSG}: {language_code}")

            community = Community.objects.filter(pk = community_id).first()

            if not community:
                return False, CustomMassenergizeError(COMMUNITY_NOT_FOUND_ERR_MSG.format(community_id))

            get_data = {'code' : language_code, 'community' : community_id}
            update_data = {'language' : language, 'community' : community, 'is_enabled' : is_enabled}

            community_language, _ = CommunitySupportedLanguage.objects.update_or_create(**get_data, defaults = update_data)

            return community_language, None
        except Exception as e:
            log.exception(e)
            return False, CustomMassenergizeError(str(e))
