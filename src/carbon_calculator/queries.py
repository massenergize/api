import jsons
from .CCConstants import VALID_QUERY, INVALID_QUERY
from .models import Question, Action

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
            self.numeric_values = {}
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

            elif q.question_type == 'Number':
                if q.minimum_value!=None:
                    self.numeric_values['minimum_value'] = q.minimum_value
                if q.maximum_value!=None:
                    self.numeric_values['maximum_value'] = q.maximum_value
                if q.typical_value!=None:
                    self.numeric_values['typical_value'] = q.typical_value
        else:
            print("ERROR: Question "+name+" was not found")


def QueryAllActions():
    pass

def QuerySingleAction(name,event_tag=""):
    try:
        qs = Action.objects.filter(name=name)
        if qs:
            category_id = qs.values("category")[0]["category"]
            q = qs[0]
            questionInfo = []
            for question in q.questions:
                if question != '':
                    qq = CalculatorQuestion(question, event_tag)
                    # a question with no text is not to be included; this is how depending on the event_tag some questions would not be asked.
                    if len(qq.questionText)>0:
                        questionInfo.append(jsons.dump(qq))

            picture = ""
            if q.picture:
                picture = q.picture.file.url

            return VALID_QUERY, {"id": q.pk, "name":q.name, "title":q.title, "description":q.description, \
                                "category":category_id, "helptext":q.helptext, "questionInfo":questionInfo, \
                                "average_points":q.average_points, "picture":picture}
        else:
            #print("ERROR: Action "+name+" was not found")
            return INVALID_QUERY, {}
    except:
        print("Failure to query action : "+name)
        return INVALID_QUERY, {}

