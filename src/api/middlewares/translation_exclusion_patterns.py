import re

TRANSLATION_EXCLUSION_PATTERNS_PER_URL = {
	"/api/campaigns.infoForUser": [re.compile(r".*\.community\.name"), re.compile(r"data\.title"), ]
}
