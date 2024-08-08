import io
import json
from querystring_parser import parser
from _main_.utils.massenergize_errors import CustomMassenergizeError
from zoneinfo import ZoneInfo
from django.utils import timezone
from datetime import timedelta
from dateutil import tz
from _main_.utils.massenergize_logger import log
import base64
import pyshorteners
from openpyxl import Workbook
from better_profanity import profanity
import datetime


def custom_timezone_info(zone="UTC"):
    if not zone:
        zone = "UTC"
    return ZoneInfo(zone)


def parse_datetime_to_aware(datetime_str=None, timezone_str='UTC'):
    """
    :param datetime_str: The string representing the datetime to parse. If not provided, the current date and time will be used.
    :param timezone_str: The string representing the timezone to apply to the parsed datetime. Defaults to 'UTC'.
    :return: An aware datetime object.
    
    """
    if not datetime_str:
        datetime_str = datetime.datetime.now()
    
    if isinstance(datetime_str, datetime.datetime):
        datetime_str = datetime_str.strftime('%Y-%m-%d %H:%M:%S')
    try:
        naive_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        naive_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    
    try:
        aware_datetime = timezone.make_aware(naive_datetime, custom_timezone_info(timezone_str))
        return aware_datetime
    except Exception as e:
        log.exception(e)
        return None


def get_date_and_time_in_milliseconds(**kwargs):
    hours = kwargs.get("hours", None)
    date = datetime.datetime.now(tz=custom_timezone_info())
    if hours:
        delta = timedelta(hours=hours)
        date = date + delta
    current_time_in_ms = date.timestamp() * 1000
    return current_time_in_ms


def get_request_contents(request, **kwargs):
    filter_out = kwargs.get("filter_out")
    try:
        if request.method != "POST":
            return request.GET.dict()

        args = {}
        if request.content_type == "application/x-www-form-urlencoded":
            args = parser.parse(request.POST.urlencode())
        elif request.content_type == "application/json":
            args = json.loads(request.body)
        elif request.content_type == "multipart/form-data":
            args = request.POST.dict()
            if request.FILES:
                for i in request.FILES.dict():
                    args[i] = request.FILES[i]
        else:
            args = request.POST.dict()

        if filter_out:
            for key in filter_out:
                args.pop(key, None)
        return args

    except Exception as e:
        log.exception(e)
        return {}


def parse_list(d):
    try:
        tmp = []
        if isinstance(d, str):
            tmp = d.strip().split(",") if d else []
        elif isinstance(d, dict):
            tmp = list(d.values())

        res = []
        for i in tmp:
            if i.isnumeric():
                res.append(i)
        return res

    except Exception as e:
        log.exception(e)
        return []

def parse_dict(d: object) -> object:
    try:
        return json.loads(d)
    except Exception as e:
        log.exception(e)
        return dict()


def parse_str_list(d):
    try:
        if d and isinstance(d, str):
            tmp = [t.strip() for t in d.strip().split(",") if t.strip()]
            return tmp
        return []
    except Exception as e:
        log.exception(e)
        return []


def parse_bool(b):
    if not b:
        return False
    return (
        (isinstance(b, bool) and b)
        or (b == "true")
        or (b == "1")
        or (b == 1)
        or (b == "True")
    )


def parse_string(s):
    try:
        s = str(s)
        if s == "undefined" or s == "null":
            return None
        return s
    except Exception as e:
        log.exception(e)
        return None


# def parse_int(b):
#     try:
#         return int(b)
#     except Exception as e:
#         log.exception(e)
#         return 1

def parse_int(b):
    if not str(b).isdigit():
        return None
    try:
        return int(b)
    except Exception as e:
        log.exception(e)
        return 1

def parse_date(d):
    try:
        if d == "undefined" or d == "null":  # providing date as 'null' should clear it
            return None
        if len(d) == 10:
            return datetime.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=custom_timezone_info())
        else:
            return datetime.datetime.strptime(d, "%Y-%m-%d %H:%M").replace(tzinfo=custom_timezone_info())

    except Exception as e:
        log.exception(e)
        return timezone.now()


def rename_field(args, old_name, new_name):
    oldVal = args.pop(old_name, None)
    if oldVal:
        args[new_name] = oldVal
    return args


def rename_fields(args, pairs):
    for old_name, new_name in pairs:
        args = rename_field(args, old_name, new_name)
    return args


def serialize_all(data, full=False, **kwargs):
    # medium = (kwargs or {}).get("medium", False)
    info = (kwargs or {}).get("info", False)
    if not data:
        return []

    if isinstance(data[0], dict):
        return data

    if full:
        return [d.full_json() for d in data]
    elif info:
        return [d.info() for d in data]
    # elif medium:
    #  return [d.medium_json() for d in data]
    return [d.simple_json() for d in data]


def serialize(data, full=False, **kwargs):
    info = (kwargs or {}).get("info", False)
    if not data:
        return {}

    if full:
        return data.full_json()
    elif info:
        return data.info()

    return data.simple_json()


def check_length(args, field, min_length=5, max_length=40):
    data = args.get(field, None)
    if not data:
        return False, CustomMassenergizeError(f"Please provide a {field} field")

    data_length = len(data)
    if data_length < min_length or data_length > max_length:
        return False, CustomMassenergizeError(
            f"{field} has to be between {min_length} and {max_length}"
        )
    return True, None


def parse_location(args):
    location = {
        "address": args.pop("address", None),
        "unit": args.pop("unit", None),
        "city": args.pop("city", None),
        "state": args.pop("state", None),
        "zipcode": args.pop("zipcode", None),
        "country": args.pop("country", "US"),
        "building": args.pop("building", None),
        "room": args.pop("room", None),
    }
    args["location"] = location
    return args


def extract_location(args):
    location = {
        "address": args.pop("address", None),
        "unit": args.pop("unit", None),
        "city": args.pop("city", None),
        "state": args.pop("state", None),
        "zipcode": args.pop("zipcode", None),
        "country": args.pop("country", "US"),
        "building": args.pop("building", None),
        "room": args.pop("room", None),
    }

    return location


# def is_value(b):
#     if b and b != "undefined" and b != "NONE":
#         return True
#     if b == "":  # an empty string is a string value
#         return True
#     return False

def is_value(b):
    if b and b not in ["undefined", "null", "None", ""]:
        return True
    return False


# def resize_image(img, options={}):
#  if options.get("is_logo", False):
#    size = options.get("size", 500)
#    width = options.get("width", 250)
#    height = options.get("height", 100)
#    dimension = (width, height)
#    new_img = cv2.resize(img, dsize=size, dim=dimension, interpolation = cv2.INTER_AREA)
#    return new_img
#  else:
#    size = options.get("size", 500)
#    new_img = cv2.resize(img, dsize=size, interpolation = cv2.INTER_AREA)
#    return new_img


def _common_name(s):
    return (" ".join(s.split("_"))).title()


def validate_fields(args, checklist):
    for field in checklist:
        if field not in args:
            return False, CustomMassenergizeError(
                f"You are missing: {_common_name(field)}"
            )
    return True, None


def get_cookie(request, key):
    cookie = request.COOKIES.get(key)
    if cookie and len(cookie) > 0:
        return cookie
    else:
        return None


def set_cookie(response, key, value):  # TODO
    print(f"----- set_cookie: {response}")
    # set cookie on response before sending
    # cookie expiration set to 1yr
    MAX_AGE = 31536000

    response.set_cookie(key, value, MAX_AGE, samesite="Strict")


def local_time():
    local_zone = tz.tzlocal()
    dt_utc = parse_datetime_to_aware()
    local_now = dt_utc.astimezone(local_zone)
    return local_now


def utc_to_local(iso_str):
    local_zone = tz.tzlocal()
    dt_utc = datetime.datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=custom_timezone_info())
    local_now = dt_utc.astimezone(local_zone)
    return local_now


def encode_data_for_URL(data):
    return base64.b64encode(json.dumps(data).encode()).decode()


def shorten_url(url):
    s = pyshorteners.Shortener()
    return s.tinyurl.short(url)



def generate_workbook_with_sheets(sheet_data):
    wb = Workbook()

    # Get the first sheet
    ws = wb.active

    # Populate the first sheet
    first_sheet_name, first_sheet = next(iter(sheet_data.items()))
    ws.title = first_sheet_name
    for row in first_sheet["data"]:
        ws.append(row)

    # Create and populate the other sheets
    for sheet_name, sheet in list(sheet_data.items())[1:]:
        ws = wb.create_sheet(title=sheet_name)
        for row in sheet["data"]:
            ws.append(row)

    buffer = io.BytesIO()
    wb.save(buffer)

    bytes_data = buffer.getvalue()
    return bytes_data




def contains_profane_words(text):
    profanity.load_censor_words()
    return profanity.contains_profanity(text)


def to_django_date(date):
    if not date:
        return None
    parsed_date = datetime.datetime.strptime(date, "%a %b %d %Y %H:%M:%S GMT%z")
    return parsed_date.date()