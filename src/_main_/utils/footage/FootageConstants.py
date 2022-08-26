

class FootageConstants:
   

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
    def forward():
        return FootageConstants.TYPES["FORWARD"]["key"]

    @staticmethod
    def is_copying(_type):
        return FootageConstants.TYPES["COPY"]["key"] == _type
        
    def copy():
        return FootageConstants.TYPES["COPY"]["key"]

    @staticmethod
    def delete():
        return FootageConstants.TYPES["DELETE"]["key"]

    @staticmethod
    def add():
        return FootageConstants.TYPES["ADD"]["key"]
        
    @staticmethod
    def remove():
        return FootageConstants.TYPES["REMOVE"]["key"]

    @staticmethod
    def sign_in():
        return FootageConstants.TYPES["SIGN_IN"]["key"]

    @staticmethod
    def approve():
        return FootageConstants.TYPES["APPROVAL"]["key"]

    @staticmethod
    def dissapprove():
        return FootageConstants.TYPES["DISAPPROVAL"]["key"]

    # ------------------------------------------------------------------------
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
        "ADD": {"key": "ADD", "name": "Add", "action_word": "added"},
        "FORWARD": {"key": "FORWARD", "name": "Forward", "action_word": "forwarded"},
        "REMOVE": {"key": "REMOVE", "name": "remove", "action_word": "removed"},
        "APPROVAL": {"key": "APPROVAL", "name": "Approval", "action_word": "approved"},
        "DISAPPROVAL": {
            "key": "DISAPPROVAL",
            "name": "Disapproval",
            "action_word": "dissapproved",
        },
    }

    ITEM_TYPES = { 
        "ACTION":{"key":"ACTION", "json_field":"is_action"},
        "EVENT":{"key":"EVENT", "json_field":"is_event"},
        "VENDOR":{"key":"VENDOR", "json_field":"is_vendor"},
        "AUTH":{"key":"AUTH", "json_field":"is_authentication"},
        "TESTIMONIAL":{"key":"TESTIMONIAL", "json_field":"is_testimonial"},
        "MEDIA":{"key":"MEDIA", "json_field":"is_media"},
        "TEAM":{"key":"TEAM", "json_field":"is_team"},
        "MESSAGE":{"key":"MESSAGE", "json_field":"is_message"},
        "COMMUNITY":{"key":"COMMUNITY", "json_field":"is_community"},
    }