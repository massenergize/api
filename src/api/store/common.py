from _main_.utils.utils import Console
from api.store.utils import getCarbonScoreFromActionRel
from database.models import UserActionRel
from django.db.models import Q


def count_action_completed_and_todos(**kwargs):
    """This function counts how many times an action has been completed, or added to todolist
    Returns an array of actions with (completed, todo, carbon_score) appended to each object

    """

    communities = kwargs.get("communities", [])
    actions = kwargs.get("actions", [])
    action_count_objects = {}
    query = None

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

    if not query:
        return []

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
