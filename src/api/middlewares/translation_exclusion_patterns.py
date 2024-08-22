import re

TRANSLATION_EXCLUSION_PATTERNS_PER_URL = {
	"/campaigns.infoForUser": [re.compile(r".*\.community\.name"), re.compile(r"data\.title"), re.compile(r".*\.key_contact.name") ]
}
