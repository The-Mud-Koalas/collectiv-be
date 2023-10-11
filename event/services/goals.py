from ..models import GoalKind


def handle_get_all_goal_kinds():
    return GoalKind.objects.all()
