import re

TRANSLATION_EXCLUSION_PATTERNS_PER_URL = {
	"/campaigns.infoForUser": [
		re.compile(r"data\.title"),
	],
	"/campaigns.technologies.info": [
		re.compile(r".*\.vendor.name"),
	],
    "/campaigns.supported_languages.list": [
        re.compile(r".*\.name"),
	],
}
