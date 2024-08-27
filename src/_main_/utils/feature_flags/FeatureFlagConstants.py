class FeatureFlagConstants:
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
    def is_for_everyone(_type):
        return FeatureFlagConstants.AUDIENCE["EVERYONE"]["key"] == _type

    @staticmethod
    def for_everyone():
        return FeatureFlagConstants.AUDIENCE["EVERYONE"]["key"]
        
    @staticmethod
    def for_all_except():
        return FeatureFlagConstants.AUDIENCE["ALL_EXCEPT"]["key"]
    
    @staticmethod
    def is_for_all_except(_type):
        return FeatureFlagConstants.AUDIENCE["ALL_EXCEPT"]["key"] == _type

    @staticmethod
    def is_for_specific_audience(_type):
        return FeatureFlagConstants.AUDIENCE["SPECIFIC"]["key"] == _type
    
    @staticmethod
    def for_specific_audience():
        return FeatureFlagConstants.AUDIENCE["SPECIFIC"]["key"]

    @staticmethod
    def is_user_frontend(_type):
        return FeatureFlagConstants.SCOPE["FRONTEND_PORTAL"]["key"] == _type

    @staticmethod
    def for_user_frontend():
        return FeatureFlagConstants.SCOPE["FRONTEND_PORTAL"]["key"]

    @staticmethod
    def for_admin_frontend():
        return FeatureFlagConstants.SCOPE["ADMIN_FRONTEND"]["key"]

 