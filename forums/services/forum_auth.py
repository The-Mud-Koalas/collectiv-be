from event.models import Event
from users.models import User


def check_authorization(user: User, event_id: str) -> bool:
    """
    This function checks if the user is authorized to perform the action.
    ----------------------------------------------------------
    user: User object
    user_id: UUID string
    event_id: UUID string

    * The user information will be taken from the firebase authentication.
    """
    event = Event.objects.get(pk=event_id)
    participation = event.get_all_type_participation_by_participant(user)
    try:
        has_left_forum = participation.get_has_left_forum()
    except:
        has_left_forum = True

    if event.creator == user:
        return True

    if participation is not None and has_left_forum is not True:
        return True

    return False
