
from task_queue.views import community_admin_nudge, super_admin_nudge


FUNCTIONS = {
    'Super admin nudge':super_admin_nudge,
    "Community Admin nudge":community_admin_nudge
}