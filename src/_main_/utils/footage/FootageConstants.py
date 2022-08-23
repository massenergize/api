from database.models import Footage


class FootageConstants():
    PLATFORMS = {
        "ADMIN_FRONTEND_PORTAL": {
            "key": "ADMIN_FRONTEND_PORTAL",
            "name": "Admin Portal",
        },
        "USER_FRONTEND_PORTAL": {
            "key": "USER_FRONTEND_PORTAL",
            "name": "User Portal",
        },
    }
    TYPES = { 
        "DELETE": {"key":"DELETE", "name":"Delete"},
        "UPDATE": {"key":"UPDATE", "name":"Update"},
        "CREATE": {"key":"CREATE", "name":"Create"},
        "MESSAGE": {"key":"MESSAGE", "name":"Message"},
        "SIGN_IN": {"key":"SIGN_IN", "name":"Sign In"},
        "APPROVAL": {"key":"APPROVAL", "name":"Approval"},
        "DISAPPROVAL": {"key":"DISAPPROVAL", "name":"Disapproval"},
    }

    @staticmethod 
    def on_admin_portal(): 
        return FootageConstants["ADMIN_FRONTEND_PORTAL"].key

    @staticmethod
    def creating(): 
        return FootageConstants["CREATE"].key

    @staticmethod
    def updating(): 
        return FootageConstants["UPDATE"].key

    @staticmethod
    def messaging(): 
        return FootageConstants["MESSAGE"].key

    @staticmethod
    def sign_in(): 
        return FootageConstants["SIGN_IN"].key

    @staticmethod
    def approved(): 
        return FootageConstants["APPROVAL"].key

    @staticmethod
    def dissapproved(): 
        return FootageConstants["DISAPPROVAL"].key
