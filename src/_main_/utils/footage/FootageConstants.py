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

    def __init__(self) -> None:
        pass

    @staticmethod 
    def on_admin_portal(): 
        return FootageConstants["ADMIN_FRONTEND_PORTAL"].key
