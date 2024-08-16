import re

TRANSLATION_EXCLUSION_PATTERNS = {
	"/api/campaigns.infoForUser":[re.compile(r".*\.community\.name"), re.compile(r"data\.title"), ]
}