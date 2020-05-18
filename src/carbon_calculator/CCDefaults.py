from .models import CalcDefault, CalcUser
import time
import timeit
import csv

def getLocality(inputs):
    id = inputs.get("user_id","")
    community = inputs.get("community","")
    #userID = inputs.get("user_id","")
    locality = "default"
    
    if id != "":
        user = CalcUser.objects.filter(id=id).first()
        if user:
            locality = user.locality

    elif community != "":
        locality = community

    return locality


def getDefault(locality, variable, defaultValue, noUpdate=False):
    return CCD.getDefault(CCD,locality, variable, defaultValue, noUpdate)

class CCD():


    DefaultsByLocality = {"default":{}} # the class variable
    try:
        num = CalcDefault.objects.all().count()
        msg = "Initializing %d Carbon Calc defaults from db" % num
        print(msg)
        start = time.time()
        startcpu = timeit.timeit()
        cq = CalcDefault.objects.all()
        for c in cq:
            if c.locality not in DefaultsByLocality:
                DefaultsByLocality[c.locality] = {}
            DefaultsByLocality[c.locality][c.variable] = c.value
        endcpu = timeit.timeit()
        end = time.time()
        msg = "Elapsed = %.3f sec, CPU = %.3f sec" % (end - start, endcpu - startcpu)
        print(msg)
    except:
        print("CalcDefault initialization skipped")

    def __init__(self):
        print("CCD __init__ called")


    def getDefault(self,locality,variable,defaultValue, noUpdate=False):
        if locality in self.DefaultsByLocality:
            if variable in self.DefaultsByLocality[locality]:
                return self.DefaultsByLocality[locality][variable]
        if variable in self.DefaultsByLocality["default"]:
            return self.DefaultsByLocality["default"][variable]
        # no defaults found.  Store the default estiamte in the database

        self.DefaultsByLocality["default"][variable] = defaultValue
        if not noUpdate:
            d = CalcDefault(locality="default", variable=variable, value=defaultValue, reference="Default value without reference")
            d.save()

        return defaultValue

    def exportDefaults(self,fileName):
        try:
            with open(fileName, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                qs = CalcDefault.objects.all()
                msg = "Exporting %d CalcDefaults to csv file %s" % (qs.count(), fileName)
                print(msg)
                rowtext = ["Variable","Locality","Value","Reference","Updated"]
                rows = [rowtext]

                for q in qs:
                    rowtext =  [q.variable, q.locality,q.value,q.reference,q.updated]
                    rows.append(rowtext)

                csvwriter.writerows(rows)

                status = True
        except:
            print("Error exporting Carbon Calculator Defaults from CSV file")
            status = False

        if csvfile:
            csvfile.close()
        return status
    def importDefaults(self,fileName):
        try:
            with open(fileName, newline='') as csvfile:
                inputlist = csv.reader(csvfile)
                first = True
                for item in inputlist:
                    if first:
                        #header = item
                        first = False
                    else:
                        if len(item)<5 or item[0] == '' or item[1] == '':
                            continue
                        qs = CalcDefault.objects.filter(variable=item[0], locality=item[1])
                        if not qs:
                            print("No "+item[0]+" for "+item[1])
                        else:    
                            qs[0].delete()

                        cd = CalcDefault(variable=item[0],
                                locality=item[1],
                                value=eval(item[2]),
                                reference=item[3],
                                updated=item[4])
                        cd.save()
            status = True
        except:
            print("Error importing Carbon Calculator Defaults from CSV file")
            status = False

        if csvfile:
            csvfile.close()
        return status