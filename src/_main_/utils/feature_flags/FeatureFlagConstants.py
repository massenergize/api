class FeatureFlagCostants:
    AUDIENCE = {
        "EVERYONE": "EVERYONE",
        "SPECIFIC": "SPECIFIC",
        "ALL_EXCEPT": "ALL_EXCEPT",
    }

    SCOPE = {
        "BACKEND": "BACKEND",
        "ADMIN_FRONTEND": "ADMIN_FRONTEND",
        "FRONTEND_PORTAL": "FRONTEND_PORTAL",
    }

    @staticmethod 
    def isForEveryone(_type): 
        return FeatureFlagCostants.AUDIENCE["EVERYONE"] == _type
    @staticmethod 
    def forEveryone(): 
        return FeatureFlagCostants.AUDIENCE["EVERYONE"]
    @staticmethod 
    def isUserFrontend(_type): 
        return FeatureFlagCostants.SCOPE["FRONTEND_PORTAL"] == _type
    @staticmethod 
    def forUserFrontend(): 
        return FeatureFlagCostants.SCOPE["FRONTEND_PORTAL"]