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
    "ACTION": {"key": "ACTION", "json_field": "is_action"},
    "EVENT": {"key": "EVENT", "json_field": "is_event"},
    "VENDOR": {"key": "VENDOR", "json_field": "is_vendor"},
    "AUTH": {"key": "AUTH", "json_field": "is_authentication"},
    "TESTIMONIAL": {"key": "TESTIMONIAL", "json_field": "is_testimonial"},
    "MEDIA": {"key": "MEDIA", "json_field": "is_media"},
    "TEAM": {"key": "TEAM", "json_field": "is_team"},
    "MESSAGE": {"key": "MESSAGE", "json_field": "is_message"},
    "COMMUNITY": {"key": "COMMUNITY", "json_field": "is_community"},
}


class FootageConstants:
    TYPES = TYPES
    ITEM_TYPES = ITEM_TYPES

    @staticmethod
    def get_type(_type):
        if not _type:
            return {}
        _type = TYPES[_type]
        return _type

    @staticmethod
    def on_admin_portal():
        return PLATFORMS["ADMIN_FRONTEND_PORTAL"]["key"]

    @staticmethod
    def on_user_portal():
        return PLATFORMS["ADMIN_FRONTEND_PORTAL"]["key"]

    @staticmethod
    def create():
        return TYPES["CREATE"]["key"]

    @staticmethod
    def update():
        return TYPES["UPDATE"]["key"]

    @staticmethod
    def message():
        return TYPES["MESSAGE"]["key"]

    @staticmethod
    def forward():
        return TYPES["FORWARD"]["key"]

    @staticmethod
    def is_copying(_type):
        return TYPES["COPY"]["key"] == _type

    def copy():
        return TYPES["COPY"]["key"]

    @staticmethod
    def delete():
        return TYPES["DELETE"]["key"]

    @staticmethod
    def add():
        return TYPES["ADD"]["key"]

    @staticmethod
    def remove():
        return TYPES["REMOVE"]["key"]

    @staticmethod
    def sign_in():
        return TYPES["SIGN_IN"]["key"]

    @staticmethod
    def approve():
        return TYPES["APPROVAL"]["key"]

    @staticmethod
    def dissapprove():
        return TYPES["DISAPPROVAL"]["key"]

    @staticmethod
    def change_type_to_boolean(obj):
        name = ITEM_TYPES[obj["item_type"]]
        if not name:
            return obj
        name = name["json_field"]
        obj[name] = True
        return obj
