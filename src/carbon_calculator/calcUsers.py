from database.models import UserProfile
from .models import Event, Group, Action, ActionPoints, Station
from .CCConstants import VALID_QUERY, INVALID_QUERY
import csv

def QueryCalcUsers(userId, args):
    id = args.get("id", None)
    email = args.get("email",None)
    if id and not userId:
        userId = id
    
    if userId or email:
        status, userInfo = QuerySingleCalcUser(userId, args)
        if status == VALID_QUERY:
            return {"status":status, "userInfo":userInfo}
        else:
            if email:               
                return {"status":status, "statusText":"User ("+email+") not found"}
            else:
                return {"status":status, "statusText":"User Id ("+userId+") not found"}
    else:
        status, userList = QueryAllCalcUsers(args)
        if status == VALID_QUERY:
            return {"status":status,"userList":userList}
        else:
            return {"status":status,"statusText":"No users found"}

def QueryAllCalcUsers(args):
    
    event = args.get('Event','')
    group = args.get('Group','')
    if event == '':
        users = UserProfile.objects.all()
    else:
        users = None
        event = Event.objects.filter(name=event).first()
        if event:
            users = event.attendees.all()

    #if users:
    #    if group:
    #         users = users.filter(group=group)

    if users:
        userInfo = []
        for q in users:
            other_info = q.other_info
            carbonSaver = other_info["CarbonSaver"]
            if not carbonSaver:
                continue

            groups = q.other_info["CarbonSaver"]["groups"]
            #for group in q.groups.all():
            #    groups.append(group.displayname)

            if q.user_info.get("minimum_age", False):
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
        qs = UserProfile.objects.filter(id=userId)
    else:
        email= args.get("email",None)
        if email:
            qs = UserProfile.objects.filter(email=email)
        else:
            qs = None

    if qs:
        # User record found
        q = qs[0]

        full_name = q.full_name
        space = full_name.find('')
        firstName = full_name[0:space]
        lastName = full_name[space+1:]
        email = q.email

        locality = "unknown"
        if q.other_info and q.other_info.get("CarbonSaver", None):

            # User has used CarbonSaver
            other_info = q.other_info
            carbonSaver = other_info.get("CarbonSaver", None)

            groups = carbonSaver.get("groups",[])

            user_info = q.user_info
            if user_info:
                locality = user_info.get("locality","unknown") 
            if not user_info or not user_info.get("minimum_age",False):
                firstName = "UnderAge"
                lastName = "Anonymous"
                email = "None"

        else:
            # First time using CarbonSaver? create necessary info
            other_info = {}
            if q.other_info:
                other_info = q.other_info

            carbonSaver = {"CarbonSaver": {"points":0, "cost":0, "savings":0}}
            other_info["CarbonSaver"] = carbonSaver
            q.other_info = other_info
            q.save()

            groups = []
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

        if points>0 and carbonSaver.get("points", 0) == 0:
            carbonSaver["points"] = points
            carbonSaver["cost"] = cost
            carbonSaver["savings"] = savings
            other_info["CarbonSaver"] = carbonSaver
            q.other_info = other_info
            q.save()

        return VALID_QUERY, {"id":q.id, "First Name":firstName, "Last Name":lastName, "e-mail":email, 
                    "Locality":locality, "Groups":groups, 
                    "Created":q.created_at, "Updated":q.updated_at,
                    "TotalPoints":points, "TotalCost":cost, "TotalSavings":savings, "ActionInfoList":actionInfoList}
    else:
        return INVALID_QUERY, {}

def CreateCalcUser(args):
# 15 Nov 2020 - Change CalcUser to use the standard UserProfile

    try:
        first_name = args.get("first_name","")
        last_name = args.get("last_name","")

        full_name = first_name + " " + last_name
        full_name = args.get("full_name", full_name)
        preferred_name = first_name + last_name[0:0]    # could do better than this

        email = args.get("email","")
        locality = args.get("locality","")
        groups = args.get("groups",[])
        minimum_age = args.get("minimum_age",False)
        accepts_tnc = args.get("accepts_terms_and_conditions", False)
        eventName = args.get("eventName","")

        newUser = UserProfile.objects.filter(email=email).first()
        #newUser = CalcUser.objects.filter(email=email).first()
        if newUser:
            # the record existed
            if full_name!="":
                newUser.full_name = full_name
            if preferred_name != "":
                newUser.preferred_name = preferred_name
            if locality != "":
                newUser.locality = locality
            newUser.minimum_age = minimum_age
            newUser.accepts_tnc = accepts_tnc

            user_info = {}
            if not newUser.user_info or newUser.user_info == '':
                user_info = {}
            else:
                user_info = newUser.user_info
            user_info["locality"] = locality
            user_info["minimum_age"] = minimum_age
            newUser.user_info = user_info

            if not newUser.other_info or newUser.other_info == '':
                other_info = {"CarbonSaver": { "events":[eventName], "groups":groups, "points":0, "cost":0, "savings":0 }}
                newUser.other_info = other_info
            else:
                other_info = newUser.other_info
                carbonSaver = other_info.get("CarbonSaver", None)
                if carbonSaver:
                    if not eventName in carbonSaver["events"]:
                        carbonSaver["events"].append(eventName)
                    for group in groups:
                        if not group in carbonSaver["groups"]:
                            carbonSaver["groups"].append(group)
                    other_info["CarbonSaver"] = carbonSaver
                else:
                    other_info['CarbonSaver'] = { 'events':[eventName], 'groups':groups, 'points':0, 'cost':0, 'savings':0 }
                newUser.other_info = other_info

            newUser.save()

        else:
            newUser = UserProfile.objects.create(
                full_name=full_name,
                preferred_name = preferred_name,
                email = email, 
                is_vendor = False,
                accepts_terms_and_conditions = accepts_tnc)

            user_Info = { 'minimum_Age':minimum_age }
            newUser.user_info = user_Info

            other_info = {'CarbonSaver': { 'events':[eventName], 'groups':groups, 'points':0, 'cost':0, 'savings':0 }}
            newUser.other_info = other_info

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
                    group1.member_list.add(newUser)
                    group1.members += 1
                    group1.save()
                #    newUser.groups.add(group1)
                #    newUser.save()
                    
        return {"id":newUser.id,"email":newUser.email, "success":True}
    except Exception as e: 
        print('CreateCalcUser: '+str(e))
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
                users = UserProfile.objects.filter(other_info)
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
                    #grouplist = user.groups.all()
                    groupList =  user.group_set.all()

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
    except Exception as e:
        print("Error exporting CalcUsers to CSV file: "+str(e))
        status = False

    if csvfile:
        csvfile.close()
    return status

def CalcUserUpdate(user_id, update):
    try:
        user = UserProfile.objects.filter(id=user_id).first()
        if user:
            carbonSaver = user.other_info.get("CarbonSaver", None)
            if carbonSaver:
                for (k,v) in update:
                    carbonSaver[k] += v
                user.save()
                return True

        return False
    except:
        return False

def CalcUserLocality(user_id):
    try:
        user = UserProfile.objects.filter(id=user_id).first()
        if user:
            locality = user.user_info.get("locality", None)
            if locality:
                return locality

        return None
    except:
        return None

