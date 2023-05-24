from fileinput import filename
from .models import CalcDefault
from .calcUsers import CalcUserLocality
from datetime import datetime
import time
import timeit
import csv
from pathlib import Path  # python3 only

def getLocality(inputs):
    id = inputs.get("user_id","")
    community = inputs.get("community","")
    #userID = inputs.get("user_id","")
    locality = "default"
    
    if id != "":
        loc = CalcUserLocality(id)
        if loc:
            locality = loc

    elif community != "":
        locality = community

    return locality


def getDefault(locality, variable, date=None):
    return CCD.getDefault(CCD,locality, variable, date)

class CCD():

    DefaultsByLocality = {"default":{}} # the class variable
    try:
        # everyone is tired of this message
        print("Initializing Carbon Calculator values")

        cq = CalcDefault.objects.all()
        for c in cq:
            # valid date is 0 if not specified
            date = '2000-01-01'
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
                    elif date == valid_date:
                        # multiple values with one date
                        print('CCDefaults: multiple values with same valid date')
                        f = True
                        break
                
                # if not inserted into list, append to the end
                if not f:
                    DefaultsByLocality[c.locality][c.variable]["valid_dates"].append(date)
                    DefaultsByLocality[c.locality][c.variable]["values"].append(c.value)


    except Exception as e:
        print(str(e))
        print("CalcDefault initialization skipped")

    def __init__(self):
        print("CCD __init__ called")


    def getDefault(self, locality, variable, date):
        if locality not in self.DefaultsByLocality:
            locality = "default"
        if variable in self.DefaultsByLocality[locality]:
            # variable found; get the value appropriate for the date
            var = self.DefaultsByLocality[locality][variable]    # not a copy
            if date==None:
                # if date not specified, use the most recent value
                value = var["values"][-1]
            else:
                for i in range(len(var["valid_dates"])):
                    valid_date = var["valid_dates"][i]
                    if valid_date < date:
                        value = var["values"][i]
            return value
        
        # no defaults found.  Signal this as an error.
        raise Exception('Carbon Calculator error: value for "'+variable+'" not found in CalcDefaults')        

    def exportDefaults(self,fileName):
        try:
            with open(fileName, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                qs = CalcDefault.objects.all()
                msg = "Exporting %d CalcDefaults to csv file %s" % (qs.count(), fileName)
                print(msg)
                rowtext = ["Variable","Locality","Value","Reference","Valid Date","Updated"]
                rows = [rowtext]

                for q in qs:
                    rowtext =  [q.variable, q.locality,q.value,q.reference,q.valid_date,q.updated]
                    rows.append(rowtext)

                csvwriter.writerows(rows)

                status = True
        except Exception as error:
            print("Error exporting Carbon Calculator Defaults from CSV file")
            print(error)
            exit()
            status = False

        if csvfile:
            csvfile.close()
        return status
    def importDefaults(self,fileName):
        csvfile = None
        try:
            status = True
            with open(fileName, newline='') as csvfile:
                inputlist = csv.reader(csvfile)
                first = True
                for item in inputlist:
                    if first:
                        t = {}
                        for i in range(len(item)):
                            it = item[i]
                            if i == 0:
                                it = 'Variable'
                            t[it] = i
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
                            valid_date = '2000-01-01'

                        #valid_date = datetime.date(valid_date)
                        valid_date = datetime.strptime(valid_date, "%Y-%m-%d").date()

                        qs = CalcDefault.objects.filter(variable=variable, locality=locality)
                        if qs:
                            qs[0].delete()

                        cd = CalcDefault(variable=variable,
                                locality=locality,
                                value=value,
                                reference=reference,
                                valid_date = valid_date,
                                updated=updated)
                        cd.save()

                        if not locality in self.DefaultsByLocality:
                            self.DefaultsByLocality[locality] = {}

                        if not variable in self.DefaultsByLocality[locality]:
                            self.DefaultsByLocality[locality][variable] = {}

                            self.DefaultsByLocality[locality][variable]["valid_dates"] = [valid_date]
                            self.DefaultsByLocality[locality][variable]["values"] = [value]
                        else:
                            f = False
                            var = self.DefaultsByLocality[locality][variable]
                            for i in range(len(var["valid_dates"])):
                                compdate = var["valid_dates"][i]
                                if type(compdate)==type('str'):
                                    compdate = datetime.strptime(compdate, "%Y-%m-%d").date()
                                if valid_date < compdate:
                                    var["valid_dates"].insert(i,valid_date)
                                    var["values"].insert(i,value)
                                    f = True
                                    break
                                elif valid_date == compdate:
                                    var["values"][i] = value
                                    f = True
                                    break
                            if not f:
                                var["valid_dates"].append(valid_date)
                                var["values"].append(value)
 
            status = True
        except Exception as error:
            print("Error importing Carbon Calculator Defaults from CSV file")
            print(error)
            exit()
            status = False
        finally:
            if csvfile:
                csvfile.close()
            return status
            