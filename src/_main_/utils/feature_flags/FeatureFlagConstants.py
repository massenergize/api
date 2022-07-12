class FeatureFlagCostants:
    AUDIENCE = {
        "EVERYONE": {"name": "Everyone", "key": "EVERYONE"},
        "SPECIFIC": {"name": "Specific", "key": "SPECIFIC"},
        "ALL_EXCEPT": {"name": "All Except", "key": "ALL_EXCEPT"},
    }

    SCOPE = {
        "BACKEND": {"name": "Backend", "key": "BACKEND"},
        "ADMIN_FRONTEND": {"name": "Admin Frontend", "key": "ADMIN_FRONTEND"},
        "FRONTEND_PORTAL": {"name": "User Frontend", "key": "USER_FRONTEND"},
    }

    @staticmethod
    def isForEveryone(_type):
        return FeatureFlagCostants.AUDIENCE["EVERYONE"]["key"] == _type

    @staticmethod
    def forEveryone():
        return FeatureFlagCostants.AUDIENCE["EVERYONE"]["key"]

    @staticmethod
    def isSpecific():
        return FeatureFlagCostants.AUDIENCE["SPECIFIC"]["key"]

    @staticmethod
    def isUserFrontend(_type):
        return FeatureFlagCostants.SCOPE["FRONTEND_PORTAL"]["key"] == _type

    @staticmethod
    def forUserFrontend():
        return FeatureFlagCostants.SCOPE["FRONTEND_PORTAL"]["key"]
    @staticmethod
    def forAdminFrontend():
        return FeatureFlagCostants.SCOPE["ADMIN_FRONTEND"]["key"]

 