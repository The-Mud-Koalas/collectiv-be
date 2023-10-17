from . import sentiment
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
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


def submit_review_and_compute_sentiment(participation, request_data):
    review_sentiment_score = sentiment.compute_sentiment_score_from_text(request_data.get('event_comment'))
    return participation.create_review(
        rating=request_data.get('event_rating'),
        comment=request_data.get('event_comment'),
        sentiment_score=review_sentiment_score
    )


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_submit_review(request_data, user):
    _validate_review_request_data(request_data)
    event = event_utils.get_event_by_id_or_raise_exception_thread_safe(request_data.get('event_id'))
    participation = event.get_all_type_participation_by_participant(user)
    _validate_participant_can_submit_review(participation)
    submit_review_and_compute_sentiment(participation, request_data)
