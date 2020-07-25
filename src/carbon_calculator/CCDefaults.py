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


def getDefault(locality, variable, defaultValue, date=None, noUpdate=False):
    return CCD.getDefault(CCD,locality, variable, defaultValue, date, noUpdate)

class CCD():


    DefaultsByLocality = {"default":{}} # the class variable
    try:
        num = CalcDefault.objects.all().count()
        msg = "Initializing %d Carbon Calc defaults from db" % num
        print(msg)
        cq = CalcDefault.objects.all()
        for c in cq:
            # valid date is 0 if not specified
            date = 0
            if c.valid_date != None:
                date = c.valid_date

            if c.locality not in DefaultsByLocality:
                DefaultsByLocality[c.locality] = {}
            if c.variable not in DefaultsByLocality[c.locality]:
                DefaultsByLocality[c.locality][c.variable] = {"valid_dates":[date], "values":[c.value]}
            else:
                # already one value for this parameter, order by dates
                f = False
                for i in range(len(DefaultsByLocality[c.locality][c.variable]["values"])):
                    valid_date = DefaultsByLocality[c.locality][c.variable]["valid_dates"][i]
                    if date < valid_date:
                        # insert value at this point
                        f = True
                        DefaultsByLocality[c.locality][c.variable]["valid_dates"].insert(i,date)
                        DefaultsByLocality[c.locality][c.variable]["values"].insert(i,c.value)
                        break
                    else if date == valid_date:
                        # multiple values with one date
                        print('CCDefaults: multiple values with same valid date')
                        f = True
                        break
                
                # if not inserted into list, append to the end
                if not f:
                    DefaultsByLocality[c.locality][c.variable]["valid_dates"].append(date)
                    DefaultsByLocality[c.locality][c.variable]["values"].append(c.value)


    except:
        print("CalcDefault initialization skipped")

    def __init__(self):
        print("CCD __init__ called")


    def getDefault(self,locality,variable,defaultValue, date, noUpdate=False):
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
                        t = {}
                        for i in range(len(item)):
                            t[item[i]] = i
                        first = False
                    else:
                        if len(item)<6 or item[0] == '' or item[1] == '':
                            continue
                        variable = item[t["Variable"]]
                        locality = item[t["Locality"]]
                        valid_date = item[t["Valid Date"]]
                        value = eval(item[t["Value"]])
                        reference = item[t["Reference"]]
                        updated = item[t["Updated"]]
                        if not valid_date or valid_date=="":
                            qs = CalcDefault.objects.filter(variable=variable, locality=locality)
                            if not qs:
                                print("No "+item[0]+" for "+item[1])
                            else:    
                                qs[0].delete()

                        cd = CalcDefault(variable=variable,
                                locality=locality,
                                value=value,
                                reference=reference,
                                valid_date = valid_date,
                                updated=updated)
                        cd.save()
            status = True
        except:
            print("Error importing Carbon Calculator Defaults from CSV file")
            status = False

        if csvfile:
            csvfile.close()
        return status