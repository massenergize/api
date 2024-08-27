import csv
import datetime
import io
from functools import reduce
from typing import List

import boto3
from django.db.models import Count, Model, Q
from django.http import FileResponse
from xhtml2pdf import pisa

from _main_.settings import AWS_S3_REGION_NAME
from _main_.utils.common import custom_timezone_info, serialize, serialize_all
from api.constants import CSV_FIELD_NAMES
from carbon_calculator.models import Action
from database.utils.common import calculate_hash_for_bucket_item
from database.models import Community, CommunityAdminGroup, Event, Media, Team, UserActionRel
from carbon_calculator.carbonCalculator import getCarbonImpact

s3 = boto3.client("s3", region_name=AWS_S3_REGION_NAME)


LAST_VISIT = "last-visit"
LAST_WEEK = "last-week"
LAST_MONTH = "last-month"
LAST_YEAR = "last-year"

NON_EXISTENT_IMAGE = "NON_EXISTENT_IMAGE"

def js_datetime_to_python(datetext):
    _format = "%Y-%m-%dT%H:%M:%SZ"
    _date = datetime.datetime.strptime(datetext, _format)
    _date = _date.replace(tzinfo=custom_timezone_info())
    return _date


def make_time_range_from_text(time_range):
    today = datetime.datetime.now()
    if time_range == LAST_WEEK:
        start_time = today - datetime.timedelta(days=7)
        end_time = today

    elif time_range == LAST_MONTH:
        start_time = today - datetime.timedelta(days=31)
        end_time = today
    elif time_range == LAST_YEAR:
        start_time = today - datetime.timedelta(days=365)
        end_time = today
    return [start_time, end_time]


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
        start_date = kwargs.get("start_date", "")
        end_date = kwargs.get("end_date", "")
        time_range = [
            js_datetime_to_python(start_date),
            js_datetime_to_python(end_date),
        ]
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
        action_carbon = getCarbonImpact(completed_action)
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
    response = FileResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename={filename}.pdf"
    return pdf_buffer.getvalue(), response


def sign_mou(mou_rich_text, user=None, date=None):
    return (
        f"""
        {mou_rich_text}
        <div> 
        <h1>Signed By</h2> 
        <h2>Name: {user.full_name}</h2> 
        <h2>Date: {date} </h2>
        </div>
    """
        if (user and date)
        else mou_rich_text
    )


def expect_media_fields(self):
    self.validator.expect("size", str).expect("size_text", str).expect(
        "description"
    ).expect("underAge", bool).expect("copyright", bool).expect(
        "copyright_att", str
    ).expect(
        "guardian_info", str
    ).expect(
        "permission_key", str
    ).expect(
        "permission_notes", str
    )
    return self


def make_media_info(args):
    """Request arg names are different from how they are stored on the media object, so this function corrects the naming and makes sure it matches the structure that is actually saved on the media object"""
    fields = [
        "copyright",
        "copyright_att",
        "underAge",
        "size",
        "size_text",
        "guardian_info",
        "permission_key", 
        "permission_notes"
    ]
    name_to_obj_name = {
        "underAge": "has_children",
        "copyright": "has_copyright_permission",
    }
    obj = {}
    for name in fields:
        value = args.pop(name, None)
        name = name_to_obj_name.get(name, name)
        if value:
            obj[name] = value
    return obj

def get_media_info(media):
    """Retrieves media info from media object"""
    if not media:
        return {}, False
    if hasattr(media, "user_upload"):
        if hasattr(media.user_upload, "info") and media.user_upload.info is not None:
            return media.user_upload.info, True
    return {}, False





def find_duplicate_items(_serialize=False, **kwargs):
    community_ids = kwargs.get("community_ids", None)
    if community_ids:
        # First, filter the Media objects that belong to the given communities
        print("Communities specified, duplicate context will be against only images in communities with ids : ",community_ids)
        media_in_communities = Media.objects.filter(user_upload__communities__id__in=community_ids)
        # Then, find the duplicate hashes in these media items
        duplicate_hashes = (
            media_in_communities.exclude(hash__exact="")
            .exclude(hash=None)
            .exclude(hash=NON_EXISTENT_IMAGE)
            .values("hash")
            .annotate(hash_count=Count("hash"))
            .filter(hash_count__gt=1)
        )
    else:
        # If no community_ids are provided, check duplicates against all the media records
        print("No communities specified, duplicate context will be against all images in the bucket....")
        duplicate_hashes = (
            Media.objects.exclude(hash__exact="")
            .exclude(hash=None)
            .exclude(hash=NON_EXISTENT_IMAGE)
            .values("hash")
            .annotate(hash_count=Count("hash"))
            .filter(hash_count__gt=1)
        )

     # Now, retrieve the media items associated with the duplicate hashes
    if community_ids: 
        duplicate_media_items = Media.objects.filter(
            hash__in=duplicate_hashes.values("hash"), user_upload__communities__id__in = community_ids
        ) 
    else: 
        duplicate_media_items = Media.objects.filter(
            hash__in=duplicate_hashes.values("hash")
        )

    return group_duplicates(duplicate_media_items, _serialize)

def group_duplicates(duplicates, _serialize=False):
    # Here, media library items that have the same hashes are grouped with the hash value as key, and the items themselves in an array
    print("group_duplicates")
    response = {}
    count = 0
    for item in duplicates:
        count = count + 1
        old = response.get(item.hash, None)
        json = item
        if _serialize:
            json = serialize(item)

        if old:
            old.append(json)
        else:
            response[item.hash] = [json]


    return response

def serial_wrapper(queryset, _serialize=False):
    if _serialize:
        return serialize_all(queryset, False, info=True)
    return queryset

def find_relations_for_item(media_item: Media, _serialize=False):
    # Given a media item, this function finds all entities that are using it on the entire platform
    relations = {
        "community_logos": [],
        "actions": [],
        "events": [],
        "vendors": [],
        "teams": [],
        "homepage": [],
        "tags":[]
    }

    if not media_item:
        return relations
    
    communities = serial_wrapper(
        media_item.community_logo.all(), _serialize
    )  # communities that use this media as their logo
    homepage = serial_wrapper(
        media_item.homepage_images.all(), _serialize
    )  # communities that use this media as their homepage image
    actions = serial_wrapper(
        media_item.actions.all(), _serialize
    )  # actions that use this media
    events = serial_wrapper(
        media_item.events.all(), _serialize
    )  # events that use this media
    vendors = serial_wrapper(
        media_item.vender_logo.all(), _serialize
    )  # vendors that use this media as their logo
    teams = serial_wrapper(
        media_item.team_logo.all(), _serialize
    )  # teams that use this media as their logo

    tags = serial_wrapper(media_item.tags.all(), _serialize)
    return {
        "community_logos": communities,
        "actions": actions,
        "events": events,
        "vendors": vendors,
        "teams": teams,
        "homepage": homepage,
        "tags": tags
    }

def merge_and_get_distinct(array1, array2, property_name, _serialize=False):
    # Merges two arrays of dictionaries based on a property and returns distinct items
    if not array1 and not array2:
        return []
    # Create a set to keep track of distinct property values
    distinct_property_values = set()
    # Create a list to store the distinct objects
    distinct_objects = []
    # Combine the two arrays
    combined_array = array1 or [] + array2 or []

    for obj in combined_array:
        property_value = obj.get(property_name, None)
        if property_value not in distinct_property_values:
            distinct_property_values.add(property_value)
            distinct_objects.append(obj)
         

    return distinct_objects

def combine_relation_objs(relObj1, relObj2, _serialize=False):
    # takes two relation objects, takes out the individal arrays (vendors, events, community_logos etc) from each, and tries to merge them into one array of distinct items
    communities = merge_and_get_distinct(
        relObj1.get("community_logos"), relObj2.get("community_logos"), "id", _serialize
    )
    actions = merge_and_get_distinct(
        relObj1.get("actions"), relObj2.get("actions"), "id", _serialize
    )
    events = merge_and_get_distinct(
        relObj1.get("events"), relObj2.get("events"), "id", _serialize
    )
    teams = merge_and_get_distinct(
        relObj1.get("teams"), relObj2.get("teams"), "id", _serialize
    )
    vendors = merge_and_get_distinct(
        relObj1.get("vendors"), relObj2.get("vendors"), "id", _serialize
    )
    homepage = merge_and_get_distinct(
        relObj1.get("homepage"), relObj2.get("homepage"), "id", _serialize
    )
    tags = merge_and_get_distinct(
        relObj1.get("tags"), relObj2.get("tags"), "id", _serialize
    )

    

    return {
        "communities": communities,
        "events": events,
        "actions": actions,
        "teams": teams,
        "vendors": vendors,
        "homepage": homepage,
        "tags":tags
    }


def resolve_relations(dupes): 
    merged_usages = find_relations_for_item(None)
    for dupe_item in dupes:
        usage = find_relations_for_item(dupe_item, True)
        merged_usages = combine_relation_objs(usage, merged_usages, True)

    disposable = serialize_all(dupes)
    return {
        "media": disposable[0],
        "usage": merged_usages,
        "disposable": disposable[1:],
    }


def get_property_in_dict(array, property_name = "id"): 
    return [ item.get(property_name) for item in array]

def get_items_by_ids(model :Model, ids):
    """
    Retrieve items of a specified model by a list of IDs.

    Parameters:
    - model (django.db.models.Model): The Django model class.
    - ids (list of int): A list of IDs to filter items by.

    Returns:
    - Queryset: A queryset containing items with the specified IDs.
    """
    if not issubclass(model, Model):
        raise ValueError("The 'model' parameter must be a valid Django model class.")

    if not ids:
        return model.objects.none()  # Return an empty queryset if the 'ids' list is empty

    return model.objects.filter(id__in=ids)


def attach_relations_to_media(usage_object): 
    media = usage_object.get("media") 
    if not usage_object or not media: 
        return None 
    
    media = Media.objects.filter(id = media.get("id")).first() 
    if not media: 
        return None 
    
    usage = usage_object.get("usage")


    communities = usage.get("communities",[])
    actions = usage.get("actions",[])
    events = usage.get("events",[])
    teams = usage.get("teams",[])
    vendors = usage.get("vendors",[])
    homepage = usage.get('homepage',[])
    tags = usage.get('tags',[])

    # Reduce them to only their ids
    communities = get_property_in_dict(communities)
    actions = get_property_in_dict(actions)
    events = get_property_in_dict(events)
    teams = get_property_in_dict(teams)
    vendors = get_property_in_dict(vendors)
    homepage = get_property_in_dict(homepage)
    tags = get_property_in_dict(tags)

    # set relationships
    media.community_logo.set(get_items_by_ids(Community,communities))
    media.actions.set(get_items_by_ids(Action,actions))
    media.events.set(get_items_by_ids(Event,events))
    media.team_logo.set(get_items_by_ids(Team,teams)) 
    media.vender_logo.set(vendors) 
    media.homepage_images.set(homepage) 
    media.tags.set(tags)

    media.save()
    media.refresh_from_db()

    return media

def create_csv_file(fieldnames :list, data : list, filename="data.csv"):
    """
    Returns: 
    - str : output.getvalue()
    """
    # Create an in-memory CSV file
    output = io.StringIO()
    csv_writer = csv.DictWriter(output, fieldnames=fieldnames)
    csv_writer.writeheader()
    for row in data:
        csv_writer.writerow(row)
    return output.getvalue()



def arrange_for_csv(usage_object: dict):
        usage_object = {} if not usage_object else usage_object

        text = ""
        count = 0

        for key, value in usage_object.items():
            length = len(value)
            count = count + length
            if length:
                if text:
                    text += f", {key}({length})"
                else:
                    text = f"{key}({length})"

        return count, text


def compile_duplicate_size(image): 
    if not image: return 0 
    tracker = {}
    _sum = 0 
    for img in image:
        url = img.file.url
        same_url =  tracker.get(url, None)
        if not same_url: 
            size = get_image_size_from_bucket(img.get_s3_key()) or 0
            _sum += size
            tracker[url] = size 

    return _sum 


def calculate_space_saved(grouped_dupes): 
    space_saved = 0
    if not grouped_dupes: 
        return space_saved
    for _, array in grouped_dupes.items():
            rest =  rest = array[1:]
            total = compile_duplicate_size(rest)
            space_saved +=total
    return space_saved

def summarize_duplicates_into_csv(grouped_dupes, filename = None, field_names = CSV_FIELD_NAMES):
        """
        Returns: 
        - csv file : output.getvalue()
        """
        csv_data = []
        for hash, array in grouped_dupes.items():
            combined = resolve_relations(array)
            usage_count, usage_summary = arrange_for_csv(combined.get("usage", {}))
            media = array[0]
            rest = array[1:]
            # total = sum([ get_image_size_from_bucket(m.get_s3_key()) for m in rest])
            total = compile_duplicate_size(rest)
            obj = {
                "media_url": media.file.url,
                "primary_media_id": media.id,  # No other criteria is used to determine which media is going to be the primary media. The first 1 is simply chosen...
                "usage_stats": usage_count,
                "usage_summary": usage_summary,
                "duplicates": ", ".join([m.file.url for m in rest]),
                "ids_of_duplicates": ", ".join([str(m.id) for m in rest]),
                "readable_compiled_size_of_duplicates": convert_bytes_to_human_readable(total),
                "compiled_size_of_duplicates" : total
            }
            csv_data.append(obj)

        filename = filename or "summary-of-duplicates"
        csv_file = create_csv_file(field_names, csv_data, filename + ".csv")

        return csv_file

def convert_bytes_to_human_readable(size):
    """
    Converts bytes into human readable image sizes.

    Parameters:
    - size (int): The size in bytes.

    Returns:
    - str: The human readable size.
    """
    # Define the units and their corresponding values
    units = {
        "B": {"value":1, "prev": "B"},
        "KB": {"value":1024, "prev": "B"},
        "MB": {"value":1024 ** 2, "prev": "KB"},
        "GB": {"value":1024 ** 3, "prev": "MB"},
        "TB": {"value":1024 ** 4, "prev": "GB"},
    }
    # Find the appropriate unit to use
    for unit in units:
        if size < units[unit].get("value"):
            if size != 0:
                unit = units[unit].get("prev")
            break
    # Calculate the size in the appropriate unit
    size /= units[unit].get("value")
    # Format the size with two decimal places
    size = "{:.2f}".format(size)

    # Return the formatted size with the unit
    return f"{size}{unit}"

def get_admins_of_communities(community_ids): 
     groups = CommunityAdminGroup.objects.filter(community__id__in = community_ids)
     admins = [g.members.all() for g in groups]
     admins = reduce(lambda x, y: list(x) + list(y), admins)
     return admins


def get_duplicate_count(grouped_dupes :dict): 
    """
        Returns: 
        - count : (int) total count of all duplicate groups together
    """
    count = 0 
    for duplicates in grouped_dupes.values(): 
        count +=len(duplicates) -1 # Subtracting 1 because one of them is the main one, and the remaining are duplicates
        
    return count

def group_disposable(original: dict, disposable: List[int]):
        """This function simply identifies which items in the disposable list share the same image as the original.
        NB: because we initially did not dynamically label uploaded images (many many years ago.. lool) there are many scenarios where a user has  uploaded the same image multiple times and because the image was the same (with name & everything), it always replaced the existing record in the bucket, but under new media records in the database.

        So many duplicate images(media records) still share the same image reference with the original media record. This is why items that share the same image reference as the chosen original need to be identified and grouped.
        Deletion for such records will be treated differently than other duplicates where the images are the same as the original, but are completely
        different uploads in terms of the reference in the s3 bucket. In such cases the images in the s3 bucket will be removed as well!
        """

        media = Media.objects.filter(pk=original.get("id")).first()
        if not media:
            return None, None
        can_delete = Media.objects.filter(pk__in=disposable)
        only_records = []
        with_image = []
        for m in can_delete:
            if m.file.name == media.file.name:
                only_records.append(m)
            else:
                with_image.append(m)

        return only_records, with_image

def remove_duplicates_and_attach_relations(hash): 
    if not hash: 
        return None
    dupes = Media.objects.filter(hash=hash)
    relations = resolve_relations(dupes)
    media_after_attaching = attach_relations_to_media(relations)
    disposables = relations.get("disposable", [])
    disposables = [m.get("id", None) for m in disposables]
    media = relations.get("media", {})
    del_only_records, del_with_image = group_disposable(media, disposables)
    # print("disposables", disposables)
    if del_only_records:
        Media.objects.filter(
            pk__in=[m.id for m in del_only_records]
        ).delete()  # This only deletes records & doesnt fire the models "delete()" function which is what actually deletes actual image from the s3 bucket

    if del_with_image:
        for m in del_with_image:
            m.delete()  # will delete record and image from s3 bucket

    return media_after_attaching


def generate_hashes(): 
    """
        Returns : Number of items that have had their hashes generated
    """
    images = Media.objects.filter(Q(hash__exact="") | Q(hash=None)).distinct()
    count = 0
    print("Generating Hashes...")
    for image in images:
        hash = calculate_hash_for_bucket_item(image.file.name)
        if hash:
            image.hash = hash
            image.save()
            count = count + 1
        else: 
            image.hash = NON_EXISTENT_IMAGE 
            image.save() 
    return count