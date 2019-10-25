from _main_.settings import firebase
import requests

auth = firebase.auth()


def signIn(userLogInInfo):
    email = userLogInInfo['email']
    password = userLogInInfo['password']
    try:
        user = auth.sign_in_with_email_and_password(email, password)
    except requests.exceptions.HTTPError as e:
        error = e.args[0].response.json()['error']
        return {"status": error['code'], "message": error['message']}
    return {"status": 200, "userId": user['localId'], "email": user['email']}


def createUser(userInfo):
    email = userInfo['email']
    password = userInfo['password']
    user = auth.create_user_with_email_and_password(email, password)
    return {"status": 200, "userId": user['localId'], "email": user['email']}
