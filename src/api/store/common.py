import datetime
import io
from django.http import FileResponse
from xhtml2pdf import pisa
import pytz
from _main_.utils.utils import Console
from api.store.utils import getCarbonScoreFromActionRel
from database.models import  UserActionRel
from django.db.models import Q
from django.utils import timezone 


LAST_VISIT = "last-visit"
LAST_WEEK = "last-week"
LAST_MONTH = "last-month"
LAST_YEAR = "last-year"

def js_datetime_to_python(datetext): 
    _format = "%Y-%m-%dT%H:%M:%SZ"
    _date = datetime.datetime.strptime(datetext, _format)
    return pytz.utc.localize(_date)

def make_time_range_from_text(time_range): 
    today = datetime.datetime.utcnow()
    if time_range == LAST_WEEK:
        start_time = today - datetime.timedelta(days=7)
        end_time = today

    elif time_range == LAST_MONTH:
        start_time = today - datetime.timedelta(days=31)
        end_time = today
    elif time_range == LAST_YEAR:
        start_time = today - datetime.timedelta(days=365)
        end_time = today 
    return [pytz.utc.localize(start_time), pytz.utc.localize(end_time)]

def count_action_completed_and_todos(**kwargs):
    """
    ### args: communities(list), actions(list), time_range(str), start_date(str), end_date(str)
    This function counts how many times an action has been completed, or added to todolist
    Returns an array of dictionaries with the following: (name,id,done_count, todo_count, carbon_score, category)
    * Given a list of communities, todo/done will be counted within only those communities. 
    * When given a list of actions, counts will only be done for only the actions given 
    * When given both (actions & communities) an AND query will be built before counting
    * And when a time range is specified, all the query combinations listed above will run within the given time range
    """
   
    communities = kwargs.get("communities", [])
    actions = kwargs.get("actions", [])
    action_count_objects = {}
    query = None
    time_range = kwargs.get("time_range") 

    # ----------------------------------------------------------------------------
    if time_range == "custom": 
        start_date = kwargs.get('start_date',"") 
        end_date = kwargs.get("end_date","") 
        time_range = [js_datetime_to_python(start_date), js_datetime_to_python(end_date)]
    else: 
        time_range = make_time_range_from_text(time_range) if time_range else []
    # ----------------------------------------------------------------------------

    if communities and not actions:
        query = Q(real_estate_unit__community__in=communities, is_deleted=False)
    elif actions and not communities:
        query = Q(action__in=actions, is_deleted=False)
    elif actions and communities:
        query = Q(
            real_estate_unit__community__in=communities,
            action__in=actions,
            is_deleted=False,
        )
     # ----------------------------------------------------------------------------

    if not query:
        return []

    # add time range specification to the query if available
    if time_range: 
        query &= Q(updated_at__range=time_range)

    completed_actions = UserActionRel.objects.filter(query).select_related(
        "action__calculator_action"
    )

    for completed_action in completed_actions:
        action_id = completed_action.action.id
        action_name = completed_action.action.title
        action_carbon = getCarbonScoreFromActionRel(completed_action)
        done = 1 if completed_action.status == "DONE" else 0
        todo = 1 if completed_action.status == "TODO" else 0

        count_obj = action_count_objects.get(action_id, None)
        if count_obj:
            count_obj["done_count"] += done
            count_obj["carbon_total"] += action_carbon
            count_obj["todo_count"] += todo
        else:
            category_obj = completed_action.action.tags.filter(
                tag_collection__name="Category"
            ).first()
            action_category = category_obj.name if category_obj else None
            action_count_objects[action_id] = {
                "id": action_id,
                "name": action_name,
                "category": action_category,
                "done_count": done,
                "carbon_total": action_carbon,
                "todo_count": todo,
            }

    return list(action_count_objects.values())






def create_pdf_from_rich_text(rich_text, filename):
    # Convert rich text to PDF
    pdf_buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    pisa.CreatePDF(io.StringIO(rich_text), dest=pdf_buffer)

    # Close the buffer and return the response
    pdf_buffer.seek(0)
    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={filename}.pdf'
    return pdf_buffer.getvalue(), response


def sign_mou(mou_rich_text, user=None, date=None): 
    return f"""
        {mou_rich_text}
        <div> 
        <h1>Signed By</h2> 
        <h2>Name: {user.full_name}</h2> 
        <h2>Date: {date} </h2>
        </div>
    """ if (user and date) else mou_rich_text


def make_media_info(args): 
    copyright_permission = args.pop("copyright", "")
    under_age = args.pop("underAge", "")
    guardian_info = args.pop("guardian_info","")
    copyright_att = args.pop("copyright_att","")
    return {
            "size": args.pop("size",""),
            "size_text": args.pop("size_text",""),
            "has_children": under_age,
            "has_copyright_permission": copyright_permission,
            "guardian_info": guardian_info,
            "copyright_att": copyright_att,
        }