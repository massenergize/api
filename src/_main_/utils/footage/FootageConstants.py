

class FootageConstants:
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
        "DELETE": {"key": "DELETE", "name": "Delete", "action_word": "deleted"},
        "UPDATE": {"key": "UPDATE", "name": "Update", "action_word": "updated"},
        "CREATE": {"key": "CREATE", "name": "Create", "action_word": "created"},
        "COPY": {"key": "COPY", "name": "Copy", "action_word": "copied"},
        "MESSAGE": {"key": "MESSAGE", "name": "Message", "action_word": "messaged"},
        "SIGN_IN": {"key": "SIGN_IN", "name": "Sign In", "action_word": "signed in"},
        "APPROVAL": {"key": "APPROVAL", "name": "Approval", "action_word": "approved"},
        "DISAPPROVAL": {
            "key": "DISAPPROVAL",
            "name": "Disapproval",
            "action_word": "dissapproved",
        },
    }

    @staticmethod
    def get_type(_type):
        if not _type:
            return {}
        _type = FootageConstants.TYPES[_type]
        return _type

    @staticmethod
    def on_admin_portal():
        return FootageConstants.PLATFORMS["ADMIN_FRONTEND_PORTAL"]["key"]

    @staticmethod
    def on_user_portal():
        return FootageConstants.PLATFORMS["ADMIN_FRONTEND_PORTAL"]["key"]

    @staticmethod
    def create():
        return FootageConstants.TYPES["CREATE"]["key"]

    @staticmethod
    def update():
        return FootageConstants.TYPES["UPDATE"]["key"]

    @staticmethod
    def message():
        return FootageConstants.TYPES["MESSAGE"]["key"]

    @staticmethod
    def copy():
        return FootageConstants.TYPES["COPY"]["key"]

    @staticmethod
    def delete():
        return FootageConstants.TYPES["DELETE"]["key"]

    @staticmethod
    def sign_in():
        return FootageConstants.TYPES["SIGN_IN"]["key"]

    @staticmethod
    def approve():
        return FootageConstants.TYPES["APPROVAL"]["key"]

    @staticmethod
    def dissapprove():
        return FootageConstants.TYPES["DISAPPROVAL"]["key"]
