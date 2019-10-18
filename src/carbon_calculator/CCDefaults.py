from .models import CalcDefault
import time
import timeit

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


def getDefault(locality, variable, defaultValue):
    return CCD.getDefault(CCD,locality, variable, defaultValue)

class CCD():
    num = CalcDefault.objects.all().count()
    msg = "Initializing %d Carbon Calc defaults from db" % num
    print(msg)
    start = time.time()
    startcpu = timeit.timeit()
    DefaultsByLocality = {"default":{}}
    cq = CalcDefault.objects.all()
    for c in cq:
        if c.locality not in DefaultsByLocality:
            print("Adding "+c.locality+" to DefaultsByLocality")
            DefaultsByLocality[c.locality] = {}
        DefaultsByLocality[c.locality][c.variable] = c.value
    endcpu = timeit.timeit()
    end = time.time()
    msg = "Elapsed = %.3f sec, CPU = %.3f sec" % (end - start, endcpu - startcpu)
    print(msg)
    print(DefaultsByLocality)

    def __init__():
        print("CCD __init__ called")

    def getDefault(self,locality,variable,defaultValue):
        if locality in self.DefaultsByLocality:
            if variable in self.DefaultsByLocality[locality]:
                return self.DefaultsByLocality[locality][variable]
        if variable in self.DefaultsByLocality["default"]:
            return self.DefaultsByLocality["default"][variable]
        # no defaults found.  Store the default estiamte in the database

        self.DefaultsByLocality["default"][variable] = defaultValue
        d = CalcDefault(locality="default", variable=variable, value=defaultValue, reference="Default value without reference")
        d.save()

        return defaultValue
