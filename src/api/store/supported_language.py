from _main_.utils.error_messages import CAMPAIGN_DOES_NOT_EXIST_ERR_MSG, MISSING_CAMPAIGN_ID_ERR_MSG, \
    MISSING_SUPPORTED_LANGUAGES_ERR_MSG
from apps__campaigns.models import Campaign
from database.models import CampaignSupportedLanguage, SupportedLanguage
from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.activity_logger import log
from typing import Tuple
from django.db import IntegrityError
from _main_.utils.constants import DEFAULT_SOURCE_LANGUAGE_CODE, INVALID_LANGUAGE_CODE_ERR_MSG
from uuid import UUID


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
                return None, CustomMassenergizeError(MISSING_CAMPAIGN_ID_ERR_MSG)
                
            campaign = Campaign.objects.get(pk=campaign_id)
            
            if not campaign:
                return None, CustomMassenergizeError(CAMPAIGN_DOES_NOT_EXIST_ERR_MSG.format(campaign_id))
            
            if not supported_languages_dict:
                return None, CustomMassenergizeError(MISSING_SUPPORTED_LANGUAGES_ERR_MSG)
            
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
                return None, CustomMassenergizeError(MISSING_CAMPAIGN_ID_ERR_MSG)
            
            campaign = None
            try:
                uuid_id = UUID(campaign_id, version=4)
                campaign = Campaign.objects.filter(id=uuid_id, is_deleted=False).first()
            except ValueError:
                campaign = Campaign.objects.filter(slug=campaign_id, is_deleted=False).first()
            
            if not campaign:
                return None, CustomMassenergizeError(CAMPAIGN_DOES_NOT_EXIST_ERR_MSG.format(campaign_id))
            
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
        