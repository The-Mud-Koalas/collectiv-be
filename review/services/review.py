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

    if not participation.has_checked_out():
        raise InvalidRequestException('Please check out from event before submitting review')


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_participant_submit_review(request_data, participant_user):
    """
    Validate review type:
        event_rating: integer
        event_comment: string optional

    Validate event exists
    Validate user is a participant/volunteer of event
    Validate user has checks out

    Submit review
    """
    _validate_review_request_data(request_data)
    request_data = communalspace_utils.trim_all_request_attributes(request_data)

    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    participation = event.get_participation_by_participant(participant_user)
    _validate_participant_can_submit_review(participation)

    participation.create_review(request_data.get('event_rating'), request_data.get('event_comment'))


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_contributor_submit_review(request_data, participant_user):
    """
    Validate review type

    Validate event exist and is a project
    Validate user is a contributor

    Submit review
    """
    _validate_review_request_data(request_data)
    request_data = communalspace_utils.trim_all_request_attributes(request_data)

    project = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    contribution = project.get_participation_by_participant(participant_user)

    contribution.create_review(request_data.get('event_rating'), request_data.get('event_comment'))
