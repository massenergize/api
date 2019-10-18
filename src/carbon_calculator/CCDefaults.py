from .models import CalcDefault

# constants
YES = "Yes"
NO = "No"
FRACTIONS = ["None","Some","Half","Most","All"]
NUM = 0   
VALID_QUERY = 0
INVALID_QUERY = -1
HEATING_SYSTEM_POINTS = 10000
SOLAR_POINTS = 6000
ELECTRICITY_POINTS = 5000


def getLocality(inputs):
    userID = inputs.get("user_id","")
    locality = "default"
    if userID != "":
        user = CalcUser.objects.get(id=userID).first()
        if user:
            locality = user.locality
    return locality


def getDefault(locality, variable, roughGuess):
    if locality in CCD.DefaultsByLocality:
        if variable in CCD.DefaultsByLocality[locality]:
            return CCD.DefaultsByLocality[locality][variable]
    if variable in CCD.DefaultsByLocality["default"]:
        return CCD.DefaultsByLocality["default"][variable]
    return roughGuess


class CCD():
    print("Start of CCD")
    DefaultsByLocality = {}
    #print(CalcDefault.objects.all().count())
    #cq = CalcDefault.objects.all()
    cq = []
    for c in cq:
        if c.locality not in DefaultsByLocality:
            print("Adding "+c.locality+" to DefaultsByLocality")
            DefaultsByLocality[c.locality] = {}
        DefaultsByLocality[c.locality][c.variable] = c.value
    print(DefaultsByLocality)

    def __init__():
        print("CCD __init__ called")

