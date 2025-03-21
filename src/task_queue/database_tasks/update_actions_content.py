import csv
import datetime
import traceback
from django.apps import apps
from _main_.utils.massenergize_logger import log
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.feature_flag_keys import UPDATE_ACTIONS_CONTENT_FF
from api.utils.constants import DATA_DOWNLOAD_TEMPLATE
from database.models import Community, Action, FeatureFlag
from carbon_calculator.models import Action as CCAction
from django.http import HttpResponse
from _main_.settings import BASE_DIR


ACTIONS_UPDATE_FILE = BASE_DIR + "/carbon_calculator/content/all-actions-update.csv"

"""
This task is used to update Action content in the database for one or more communities.
There are two parts to this:
1. Generate a report of the contents that need to be fixed with the following information
    a. Community: the community the Action belongs to
    b. Action name: the name or title of the content
    c. Carbon Calculator action and old carbon calculator action, if differnt
    d. Impact, cost or category tag and old impact/cost/category tag, if different
2. Update the link between Action and CCAction, to be correct in all cases.
3. As appropriate - delete a number of garbage actions with no redeeming features
"""

def write_to_csv(data):
    response = HttpResponse(content_type="text/csv")
    writer = csv.DictWriter(response, fieldnames=["Community", "Action Name", "CCAction", "Impact", "Cost"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return response.content


def update_actions_content(task=None):
    try:
        data = []
        communities = Community.objects.filter(is_deleted=False)

        # check if update feature enabled, otherwise will just report
        flag = FeatureFlag.objects.filter(key=UPDATE_ACTIONS_CONTENT_FF).first()
        if not flag or not flag.enabled():
            update_enabled = False
        else:
            update_enabled = True
            enabled_communities = flag.enabled_communities(communities)

        # ccActions = CCAction.objects.filter(is_deleted=False) - when we implement ccAction deletion
        ccActions = CCAction.objects.all()

        # open the all-actions-content.csv file which will drive the updates
        with open(ACTIONS_UPDATE_FILE, newline='') as csvfile:
            inputlist = csv.reader(csvfile)
            first = True
            num = 0

            # loop over lines in the file
            for item in inputlist:
                if first:   # header line
                    t = {}
                    for i in range(len(item)):
                        if i==0:
                            item[i] = 'Name'
                        t[item[i]] = i
                    first = False
                else:
                    community_name = item[0]
                    community = None
                    if community_name != '':
                        community = communities.filter(name=community_name)
                        if not community:
                            continue    # commmunity not in this database
                        community = community.first()
                        


                    action_title = item[t["Action"]]
                    impact = item[t["Impact"]]
                    cost = item[t["Cost"]]
                    #category = item[t["Category"]]
                    ccActionName = item[t["Carbon Calculator Action"]]

                    # locate the Action from title and community.  There could be multiple versions with same name
                    actions = Action.objects.filter(title=action_title, community=community, is_deleted=False)
                    for action in actions:

                        # check whether action has correct calculator_action, impact and cost
                        if not action.calculator_action or action.calculator_action.name != ccActionName:
                            
                            # add line to report
                            line = {
                                "Community": community_name,
                                "Action Name": action_title,
                                "CCAction": ccActionName,
                                "Impact": impact,
                                "Cost": cost,
                                }
                            data.append(line)
                            
                            if update_enabled:
                                if not community or community in enabled_communities:
                                    if ccActionName == "DELETE":
                                        # if calculator_action is DELETE, mark for deletion
                                        action.is_deleted = True
                                    else:
                                        # set calculator_action,
                                        ccAction = ccActions.filter(name=ccActionName)
                                        if not ccAction:
                                            print("Carbon calculator action '"+ccActionName+"' does not exist")
                                            continue
                                        action.calculator_action = ccAction.first()
                                    action.save()

                             
        if len(data) > 0:
            report =  write_to_csv(data)
            temp_data = {'data_type': "Content Spacing", "name":task.creator.full_name if task.creator else "admin"}
            file_name = "Update-Actions-Report-{}.csv".format(datetime.datetime.now().strftime("%Y-%m-%d"))
            send_massenergize_email_with_attachments(DATA_DOWNLOAD_TEMPLATE,temp_data,[task.creator.email], report, file_name)
        res = {
            "scope":"SADMIN",
            "audience": task.creator.email
        }
        return res, None
    except Exception as e:
      stack_trace =  traceback.format_exc()
      log.exception(e)
      return None, stack_trace
  
    

