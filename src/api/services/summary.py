from _main_.utils.common import serialize, serialize_all
from _main_.utils.footage.spy import Spy
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from api.store.summary import SummaryStore
from typing import Tuple


class SummaryService:
    """
    Service Layer for all the summaries
    """

    def __init__(self):
        self.store = SummaryStore()

    def next_steps_for_admins(
        self, context, args
    ) -> Tuple[tuple, MassEnergizeAPIError]:
        content, err = self.store.next_steps_for_admins(context, args)

        if err:
            return None, err

        last_visit = content.get("last_visit")
        testimonials = content.get("testimonials", [])
        messages = content.get("messages", [])
        team_messages = content.get("team_messages", [])
        users = content.get("users", [])
        teams = content.get("teams", [])
        done_int = content.get("done_interactions", [])
        todo_int = content.get("todo_interactions", [])

        content = {
            "testimonials": {"count": len(testimonials), "data": list(testimonials)},
            "teams": {"count": len(teams), "data": list(teams)},
            "messages": {"count": len(messages), "data": list(messages)},
            "team_messages": {"count": len(team_messages), "data": list(team_messages)},
            "done_interactions": {"count": len(done_int), "data": list(done_int)},
            "todo_interactions": {"count": len(todo_int), "data": list(todo_int)},
            "users": {
                "count": len(users),
                "description": f"All new users since last visit - {last_visit.created_at}",
                "data": list(users),
                "last_visit": serialize(last_visit),
            },
        }

        return content, None

    def summary_for_community_admin(
        self, context, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        summary, err = self.store.summary_for_community_admin(context, community_id)
        if err:
            return None, err
        return summary, None

    def summary_for_super_admin(self, context) -> Tuple[list, MassEnergizeAPIError]:
        summary, err = self.store.summary_for_super_admin(context)
        if err:
            return None, err
        return summary, None
