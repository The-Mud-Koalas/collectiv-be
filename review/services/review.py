from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from communalspace import utils as communalspace_utils
from django.core.exceptions import ObjectDoesNotExist
from event.services import utils as event_utils


def _validate_review_request_data(request_data):
    if not isinstance(request_data.get('event_rating'), int):
        raise InvalidRequestException('Event rating must be an integer')

    if request_data.get('event_rating') <= 0:
        raise InvalidRequestException('Event rating must be a positive integer')

    if request_data.get('event_comment') is not None and not isinstance(request_data.get('event_comment'), str):
        raise InvalidRequestException('Event comment must be of type string')


def _validate_participant_can_submit_review(participation):
    if participation is None:
        raise InvalidRequestException('User is not a participant of event')

    if not participation.can_submit_review():
        raise InvalidRequestException('Participant has not attended event or has submitted a review')


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_submit_review(request_data, user):
    _validate_review_request_data(request_data)
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    participation = event.get_all_type_participation_by_participant(user)
    _validate_participant_can_submit_review(participation)
    participation.create_review(request_data.get('event_rating'), request_data.get('event_comment'))
