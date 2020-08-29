from .models import CalcUser, Event, Group, Action, ActionPoints, Station
from .CCConstants import VALID_QUERY, INVALID_QUERY
import csv

def QueryCalcUsers(userId, args):
    id = args.GET.get("id", None)
    email = args.GET.get("email",None)
    if id and not userId:
        userId = id
    
    if userId or email:
        status, userInfo = QuerySingleCalcUser(userId, args)
        if status == VALID_QUERY:
            return {"status":status, "userInfo":userInfo}
        else:
            if userId:               
                return {"status":status, "statusText":"User Id ("+userId+") not found"}
            else:
                return {"status":status, "statusText":"User ("+email+") not found"}
    else:
        status, userList = QueryAllCalcUsers(args)
        if status == VALID_QUERY:
            return {"status":status,"userList":userList}
        else:
            return {"status":status,"statusText":"No users found"}

def QueryAllCalcUsers(args):
    
    event = args.GET.get('Event','')
    group = args.GET.get('Group','')
    if event == '':
        users = CalcUser.objects.all()
    else:
        users = None
        event = Event.objects.filter(name=event).first()
        if event:
            users = event.attendees.all()

    if users:
        if group:
             users = users.filter(group=group)

    if users:
        userInfo = []
        for q in users:

            groups = []
            for group in q.groups.all():
                groups.append(group.displayname)

            if q.minimum_age:
                firstName = q.first_name
                lastName = q.last_name
                email = q.email
            else:
                firstName = "UnderAge"
                lastName = "Anonymous"
                email = "None"

            #actions the user has committed to
            actionInfoList = []
            points = cost = savings = 0.
            actions = ActionPoints.objects.filter(user=q.id)
            if actions:
                for action in actions:
                    points += action.points
                    cost += action.cost
                    savings += action.savings
                    actionInfo = {"action":action.action, "choices":action.choices,"points":action.points,
                                "cost":action.cost, "savings":action.savings, "date":action.created_date}
                    actionInfoList.append(actionInfo)


            info = {"id":q.id, "First Name":firstName, "Last Name":lastName, "e-mail":email, 
                    "Locality":q.locality, "Groups":groups, 
                    "Created":q.created_at, "Updated":q.updated_at,
                    "TotalPoints":points, "TotalCost":cost, "TotalSavings":savings, "ActionInfoList":actionInfoList}
            userInfo.append(info)
        return VALID_QUERY, userInfo
    else:
        return INVALID_QUERY, []

def QuerySingleCalcUser(userId,args):
    if userId:
        qs = CalcUser.objects.filter(id=userId)
    else:
        email= args.GET.get("email",None)
        if email:
            qs = CalcUser.objects.filter(email=email)
        else:
            qs = None

    if qs:
        q = qs[0]
        groups = []
        for group in q.groups.all():
            groups.append(group.displayname)

        if q.minimum_age:
            firstName = q.first_name
            lastName = q.last_name
            email = q.email
        else:
            firstName = "UnderAge"
            lastName = "Anonymous"
            email = "None"

        #actions the user has committed to
        actionInfoList = []
        points = cost = savings = 0.
        actions = ActionPoints.objects.filter(user=userId)
        if actions:
            for action in actions:
                points += action.points
                cost += action.cost
                savings += action.savings
                actionInfo = {"action":action.action, "choices":action.choices,"points":action.points,
                            "cost":action.cost, "savings":action.savings, "date":action.created_date}
                actionInfoList.append(actionInfo)

        if points>0 and q.points==0:
            q.points = points
            q.cost = cost
            q.savings = savings
            q.save()

        return VALID_QUERY, {"id":q.id, "First Name":firstName, "Last Name":lastName, "e-mail":email, 
                    "Locality":q.locality, "Groups":groups, 
                    "Created":q.created_at, "Updated":q.updated_at,
                    "TotalPoints":points, "TotalCost":cost, "TotalSavings":savings, "ActionInfoList":actionInfoList}
    else:
        return INVALID_QUERY, {}

def CreateCalcUser(args):

    try:
        first_name = args.get("first_name","")
        last_name = args.get("last_name","")
        email = args.get("email","")
        locality = args.get("locality","")
        groups = args.get("groups",[])
        minimum_age = args.get("minimum_age",False)
        accepts_tnc = args.get("accepts_terms_and_conditions", False)
        eventName = args.get("eventName","")

        newUser = CalcUser.objects.filter(email=email).first()
        if newUser:

            if first_name!="":
                newUser.first_name = first_name
            if last_name != "":
                newUser.last_name = last_name
            if locality != "":
                newUser.locality = locality
            newUser.minimum_age = minimum_age
            newUser.accepts_tnc = accepts_tnc

            newUser.save()

        else:
            newUser = CalcUser(first_name=first_name,
                            last_name = last_name,
                            email =email, 
                            locality = locality,
                            minimum_age = minimum_age,
                            accepts_terms_and_conditions = accepts_tnc)

            newUser.save()                

        if eventName != "":
            event = Event.objects.filter(name=eventName).first()
            if event:
                event.attendees.add(newUser)
                event.save()

        if groups != []:
            for group in groups:
                group1 = Group.objects.filter(name=group).first()
                if group1:
                    newUser.groups.add(group1)
                    newUser.save()
                    
        return {"id":newUser.id,"email":newUser.email, "success":True}
    except:
        error = {"success":False}
        return error

def ExportCalcUsers(fileName, event):
    try:
        status = True
        with open(fileName, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)

            rowtext = ["First Name","Last Name","e-mail","Locality","Groups","Over13","AcceptsTNC","Created","Updated"]
            actionList = []
            if event=='':   #all events
                users = CalcUser.objects.all()
                actions = Action.objects.all()
                for action in actions:
                    rowtext.append(action.name)
                    rowtext.append(action.name+"-choices")
                    actionList.append(action.name)
            else:
                users = None
                event = Event.objects.filter(name=event).first()
                if event:
                    users = event.attendees.all()
                    for station in event.stationslist:
                        station = Station.objects.filter(name=station).first()
                        if station:
                            for action in station.actions:
                                rowtext.append(action)
                                rowtext.append(action+"-choices")
                                actionList.append(action)

            
            rows = [rowtext]

            if users:
                msg = "Exporting %d CalcUsers to csv file %s" % (users.count(), fileName)
                print(msg)
                for user in users:
                    groups = []
                    grouplist = user.groups.all()
                    if grouplist:
                        for group in grouplist:
                            groups.append(group.displayname)
                    
                    rowtext =  [user.first_name, user.last_name, user.email, user.locality, 
                                groups, user.minimum_age,user.accepts_terms_and_conditions, 
                                user.created_at, user.updated_at]


                    userActions = ActionPoints.objects.filter(user=user)
                    if userActions:
                        for action in actionList:
                            userAction = userActions.filter(action=action).first()
                            if userAction:
                                rowtext.append(userAction.points)
                                rowtext.append(userAction.choices)
                            else:
                                rowtext.append("")
                                rowtext.append("")
                    rows.append(rowtext)
                csvwriter.writerows(rows)
    except:
        print("Error exporting CalcUsers to CSV file")
        status = False

    if csvfile:
        csvfile.close()
    return status
