from fileinput import filename
from .models import CalcDefault
from datetime import datetime
from django.utils import timezone
import csv

current_tz = timezone.get_current_timezone()

def getLocality(inputs):

    community = inputs.get("community","")
    locality = "default"
    
    if community != "":
        locality = community

    return locality


def localized_time(time_string):
    # Airtable changed default time format, unexpectedly.  Make it work but protect iin case it changes backj
    ind = time_string.find('/')
    if ind>0:   # new format 11/1/2023
        time = datetime.strptime(time_string, '%m/%d/%y  %H:%M')
    else:   # old format 2023-10-01
        time = datetime.strptime(time_string, '%Y-%m-%d  %H:%M')

    return time.replace(tzinfo=current_tz)

def date_import(date_string):
    # Airtable changed default time format, unexpectedly.  Make it work but protect iin case it changes backj
    ind = date_string.find('/')
    if ind>0:   # new format 11/1/2023
        date = datetime.strptime(date_string, '%m/%d/%y')
    else:   # old format 2023-10-01
        date = datetime.strptime(date_string, '%Y-%m-%d')
    return date.date()

def getDefault(loc_options, variable, date=None, default=None):
    return CCD.getDefault(CCD, loc_options, variable, date, default=default)

def removeDuplicates():
    # assuming which duplicate is removed doesn't matter...
    for row in CalcDefault.objects.all().reverse():
        if CalcDefault.objects.filter(variable=row.variable, locality=row.locality, valid_date=row.valid_date).count() > 1:
            row.delete()

class CCD():
    DefaultsByLocality = {"default":{}} # the class variable

    # This initialization routine runs when database ready to access
    # Purpose: load Carbon Calculator constants into DefaultByLocality for routine access
    # For each variable, there is a list of values for different localities and valid_dates, ordered by date
    def loadDefaults(self):
        self.DefaultsByLocality = {"default":{}} # the class variable
        try:
            cq = CalcDefault.objects.all()
            for c in cq:
                # valid date is 0 if not specified
                date = datetime.strptime('2000-01-01','%Y-%m-%d').date()
                if c.valid_date != None:
                    date = c.valid_date

                if c.locality not in self.DefaultsByLocality:
                    self.DefaultsByLocality[c.locality] = {}
                if c.variable not in self.DefaultsByLocality[c.locality]:
                    self.DefaultsByLocality[c.locality][c.variable] = {"valid_dates":[date], "values":[c.value]}
                else:
                    # already one value for this parameter, order by dates
                    found = False
                    for i in range(len(self.DefaultsByLocality[c.locality][c.variable]["values"])):
                        valid_date = self.DefaultsByLocality[c.locality][c.variable]["valid_dates"][i]
                        if date < valid_date:
                            # insert value at this point
                            found = True
                            self.DefaultsByLocality[c.locality][c.variable]["valid_dates"].insert(i,date)
                            self.DefaultsByLocality[c.locality][c.variable]["values"].insert(i,c.value)
                            break
                        elif date == valid_date:
                            # multiple values with one date; skip
                            found = True
                            break
                        
                    # if not inserted into list, append to the end
                    if not found:
                        self.DefaultsByLocality[c.locality][c.variable]["valid_dates"].append(date)
                        self.DefaultsByLocality[c.locality][c.variable]["values"].append(c.value)

        except Exception as e:
            print(str(e))
            print("CalcDefault initialization skipped")

    def getDefault(self, loc_options, variable, date, default=None):
        # load default values if they haven't yet been loaded
        if self.DefaultsByLocality["default"]=={}:
            self.loadDefaults(self)

        # eliminate any location options which aren't tracked
        options = []
        for locality in loc_options:
            if locality in self.DefaultsByLocality:
                options.append(locality)
        # default is the standard option
        options.append("default")

        for locality in options:
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
            
        # if a default value was specified, return it
        if default:
            return default
        # no defaults specified.  Signal this as an error.
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
        print("Updating Carbon Calculator constant values.")
        removeDuplicates()
        try:
            status = True
            with open(fileName, newline='') as csvfile:
                reader = csv.reader(csvfile)

                # dictionary of column indices by heading
                column_index = {}
                headers = next(reader, None)
                for index in range(len(headers)):
                    heading = headers[index] if index!=0 else 'Variable'
                    column_index[heading] = index

                num = 0
                for item in reader:
                    if len(item)<6 or item[0] == '' or item[1] == '':
                        continue

                    variable = item[column_index["Variable"]]
                    locality = item[column_index["Locality"]]
                    valid_date = item[column_index["Valid Date"]]
                    value = eval(item[column_index["Value"]])
                    reference = item[column_index["Reference"]]
                    updated = localized_time(item[column_index["Updated"]])

                    if not valid_date or valid_date=="":
                        valid_date = '2000-01-01'

                    valid_date = date_import(valid_date)

                    # update the default value for this variable, localith and valid_date
                    qs, created = CalcDefault.objects.update_or_create(
                        variable=variable, 
                        locality=locality,
                        valid_date=valid_date,
                        defaults={
                            'value':value,
                            'reference':reference,
                            'updated':updated
                        })
                    if created:
                        num += 1

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
                if num>0:
                    msg = "Imported %d Carbon Calculator Defaults" % num
                else:
                    msg = "Carbon Calculator default values updated"
                print(msg)       
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
            