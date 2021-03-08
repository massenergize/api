import jwt
from http.cookies import SimpleCookie
from datetime import datetime
from _main_.settings import SECRET_KEY

def setupCC(client):
    client.post('/cc/import',
            {   "Confirm": "Yes",
                "Actions":"carbon_calculator/content/Actions.csv",
                "Questions":"carbon_calculator/content/Questions.csv",
                "Stations":"carbon_calculator/content/Stations.csv",
                "Groups":"carbon_calculator/content/Groups.csv",
                "Organizations":"carbon_calculator/content/Organizations.csv",
                "Events":"carbon_calculator/content/Events.csv",
                "Defaults":"carbon_calculator/content/Defaults.csv"
                })

def signinAs(client, user):

    if user:
      print("Sign in as " + user.full_name)
      dt = datetime.now()
      dt.microsecond

      payload = {
          "user_id": str(user.id), 
          "email": user.email,
          "is_super_admin": user.is_super_admin, 
          "is_community_admin": user.is_community_admin,
          "iat": dt.microsecond,
          "exp": dt.microsecond+1000000000,
      }

      the_token = jwt.encode(
          payload, 
          SECRET_KEY, 
          algorithm='HS256'
      ).decode('utf-8')

      client.cookies = SimpleCookie({'token': the_token})

    else:
      print("No user signed in")
      client.cookies = SimpleCookie({'token': ""})
