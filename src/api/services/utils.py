import requests
import json, jwt
from firebase_admin import auth

from _main_.settings import SECRET_KEY


def send_slack_message(webhook, body):
    # fix for sending to Super Admin webhook.
    # it needs to have a text field, so just stick the json string in there
    if not body.get("text", None):
        body["text"] = json.dumps(body)

    r = requests.post(url=webhook, data=json.dumps(body))
    return r


def make_token(user, firebase_token):
    try:
        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "is_super_admin": user.is_super_admin,
            "is_community_admin": user.is_community_admin,
            "iat": firebase_token.get("iat"),
            "exp": firebase_token.get("exp"),
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256").decode("utf-8")

        return token, None
    except Exception as e:
        return None, e
