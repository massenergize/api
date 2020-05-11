import jsons
from .CCConstants import VALID_QUERY, INVALID_QUERY
from .models import Question, Event, Action, Station, Group

class CalculatorQuestion:
    def __init__(self, name, event_tag=None):
        self.name = name

        qs = None
        # first look for specific question with tag
        if event_tag and len(event_tag)>0:
            suffix = '<' + event_tag + '>'
            qs = Question.objects.filter(name=name+suffix)

        if not qs:
           qs = Question.objects.filter(name=name)

        if qs:
            q = qs[0]
            self.category = q.category
            self.questionText = q.question_text
            self.questionType = q.question_type
            self.responses = []
            if q.question_type == 'Choice':
                if q.response_1 != '':
                    response = {'text':q.response_1}
                    if len(q.skip_1)>0:
                        response['skip']=q.skip_1
                    self.responses.append(response)
                if q.response_2 != '':
                    response = {'text':q.response_2}
                    if len(q.skip_2)>0:
                        response['skip']=q.skip_2
                    self.responses.append(response)
                if q.response_3 != '':
                    response = {'text':q.response_3}
                    if len(q.skip_3)>0:
                        response['skip']=q.skip_3
                    self.responses.append(response)
                if q.response_4 != '':
                    response = {'text':q.response_4}
                    if len(q.skip_4)>0:
                        response['skip']=q.skip_4
                    self.responses.append(response)
                if q.response_5 != '':
                    response = {'text':q.response_5}
                    if len(q.skip_5)>0:
                        response['skip']=q.skip_5
                    self.responses.append(response)
                if q.response_6 != '':
                    response = {'text':q.response_6}
                    if len(q.skip_6)>0:
                        response['skip']=q.skip_6
                    self.responses.append(response)
        else:
            print("ERROR: Question "+name+" was not found")

def QueryEvents(event=None):
    if event:
        status, eventInfo = QuerySingleEvent(event)
        if status == VALID_QUERY:
            return {"status":status, "eventInfo":eventInfo}
        else:               
            return {"status":status, "statusText":"Event ("+event+") not found"}
    else:
        status, eventList = QueryAllEvents()
        if status == VALID_QUERY:
            return {"status":status,"eventList":eventList}
        else:
            return {"status":status,"statusText":"No events found"}

def QueryAllEvents():
    qs = Event.objects.all()
    if qs:
        eventInfo = []
        for q in qs:
            info = {"name":q.name, "displayname":q.displayname, "datetime":q.datetime, "location":q.location}
            eventInfo.append(info)
        return VALID_QUERY, eventInfo
    else:
        return INVALID_QUERY, []

def QuerySingleEvent(event):
    qs = Event.objects.filter(name=event)
    if qs:
        q = qs[0]
        host_logo_url = sponsor_logo_url = ""
        if q.host_logo:
            host_logo_url = q.host_logo.file.url
        if q.sponsor_logo:
            sponsor_logo_url = q.sponsor_logo.file.url

        stationsList = []
        for station in q.stationslist:
            stat, stationInfo = QuerySingleStation(station, q.event_tag)
            if stat == VALID_QUERY:
                stationsList.append(stationInfo)

        groupsList = []
        for group in q.groups.all():
            stat, groupInfo = QuerySingleGroup(group.name)
            if stat == VALID_QUERY:
                groupsList.append(groupInfo)

        communitiesList = []
        attendees = q.attendees.all()
        totalPoints = totalSavings = 0.
        for calcuser in q.attendees.all():
            totalPoints += calcuser.points
            totalSavings += calcuser.savings
            community = calcuser.locality
            if community not in communitiesList:
                communitiesList.append(community)
        communitiesList.sort()

        return VALID_QUERY, {"name":q.name, "displayname":q.displayname, "datetime":q.datetime, "location":q.location,"stations":stationsList,
                "groups":groupsList,"communities":communitiesList,
                "attendees":attendees.count(),"points":totalPoints, "savings":totalSavings,
                "host_org":q.host_org, "host_contact":q.host_contact, "host_email":q.host_email, "host_phone":q.host_phone,"host_url":q.host_url,"host_logo":host_logo_url,
                "sponsor_org":q.sponsor_org, "sponsor_url":q.sponsor_url,"sponsor_logo":sponsor_logo_url}
    else:
        return INVALID_QUERY, {}

def QueryEventSummary(event=None):
    if event:
        status, eventInfo = QuerySingleEventSummary(event)
        if status == VALID_QUERY:
            return {"status":status, "eventInfo":eventInfo}
        else:               
            return {"status":status, "statusText":"Event ("+event+") not found"}
    else:
        status, eventList = QueryAllEventsSummary()
        if status == VALID_QUERY:
            return {"status":status,"eventList":eventList}
        else:
            return {"status":status,"statusText":"No events found"}

def QueryAllEventsSummary():
    qs = Event.objects.all()
    if qs:
        eventInfo = []
        for q in qs:
            event = q.name
            status, info = QuerySingleEventSummary(event)
            if status==VALID_QUERY:
                eventInfo.append(info)
            else:
                return INVALID_QUERY, []
        return VALID_QUERY, eventInfo
    else:
        return INVALID_QUERY, []


def QuerySingleEventSummary(event):
    qs = Event.objects.filter(name=event)
    if qs:
        q = qs[0]

        groupsList = []
        for group in q.groups.all():
            stat, groupInfo = QuerySingleGroup(group.name)
            if stat == VALID_QUERY:
                groupsList.append(groupInfo)

        communitiesList = []
        attendees = q.attendees.all()
        totalPoints = totalSavings = 0.
        for calcuser in q.attendees.all():
            totalPoints += calcuser.points
            totalSavings += calcuser.savings
            community = calcuser.locality
            if community not in communitiesList:
                communitiesList.append(community)
        communitiesList.sort()

        return VALID_QUERY, {"name":q.name, "displayname":q.displayname, "datetime":q.datetime, "location":q.location,
                "groups":groupsList,"communities":communitiesList,
                "attendees":attendees.count(),"points":totalPoints, "savings":totalSavings,}
    else:
        return INVALID_QUERY, {}

def QueryAllActions():
    pass

def QuerySingleAction(name,event_tag=""):
    try:
        qs = Action.objects.filter(name=name)
        if qs:
            q = qs[0]

            questionInfo = []
            for question in q.questions:
                qq = CalculatorQuestion(question, event_tag)
                # a question with no text is not to be included; this is how depending on the event_tag some questions would not be asked.
                if len(qq.questionText)>0:
                    questionInfo.append(jsons.dump(qq))

            picture = ""
            if q.picture:
                picture = q.picture.file.url

            return VALID_QUERY, {"id": q.pk, "name":q.name, "description":q.description, "helptext":q.helptext, "questionInfo":questionInfo, \
                                "average_points":q.average_points, "picture":picture}
        else:
            print("ERROR: Action "+name+" was not found")
            return INVALID_QUERY, {}
    except:
        print("Failure to query action : "+name)
        return INVALID_QUERY, {}

def QueryStations(station=None):
    if station:
        status, stationInfo = QuerySingleStation(station)
        if status == VALID_QUERY:
            return {"status":status, "stationInfo":stationInfo}
        else:               
            return {"status":status, "statusText":"Station ("+station+") not found"}
    else:
        status, stationInfo = QueryAllStations()
        if status == VALID_QUERY:
            return {"status":status,"stationList":stationInfo}
        else:
            return {"status":status,"statusText":"No stations found"}

def QueryAllStations():
    qs = Station.objects.all()
    if qs:
        stationInfo = []
        for q in qs:
            info = {"name":q.name, "displayname":q.displayname}
            stationInfo.append(info)
        return VALID_QUERY, stationInfo
    else:
        return INVALID_QUERY, []

def QuerySingleStation(station, event_tag=None):
    qs = Station.objects.filter(name=station)
    if qs:
        q = qs[0]

        actionsList = []
        for action in q.actions:
            stat, actionInfo = QuerySingleAction(action, event_tag)
            if stat == VALID_QUERY:
                actionsList.append(actionInfo)

        icon = ""
        if q.icon:
            icon = q.icon.file.url

        return VALID_QUERY, {"name":q.name, "displayname":q.displayname, "description":q.description, "icon":icon, "actions":actionsList}
    else:
        return INVALID_QUERY, {}


def QueryGroups(group=None):
    if group:
        status, groupInfo = QuerySingleGroup(group)
        if status == VALID_QUERY:
            return {"status":status, "groupInfo":groupInfo}
        else:               
            return {"status":status, "statusText":"Group ("+group+") not found"}
    else:
        status, groupInfo = QueryAllGroups()
        if status == VALID_QUERY:
            return {"status":status,"groupList":groupInfo}
        else:
            return {"status":status,"statusText":"No groups found"}

def QueryAllGroups():
    qs = Group.objects.all()
    if qs:
        groupInfo = []
        for q in qs:
            info = {"name":q.name, "displayname":q.displayname, "members":q.members}
            groupInfo.append(info)
        return VALID_QUERY,groupInfo
    else:
        return INVALID_QUERY, []    

def QuerySingleGroup(group):
    qs = Group.objects.filter(name=group)
    if qs:
        q = qs[0]
        return VALID_QUERY,{"name":q.name, "displayname":q.displayname, "description":q.description, 
                "members":q.members, "points":q.points, "savings":q.savings}
    else:
        return INVALID_QUERY, {}
