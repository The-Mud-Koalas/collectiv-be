from ..models import EventReport
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from django.core.exceptions import ObjectDoesNotExist
from event.services import utils as event_utils


def _validate_event_report_request(request_data):
    if not isinstance(request_data.get('remarks'), str):
        raise InvalidRequestException('Remarks for report must exists')


def _validate_user_can_report_event(user, event):
    if EventReport.objects.filter(event=event, reporter=user).exists():
        raise InvalidRequestException('A report for event has been submitted by the user')


def _create_report(event, reporter, remarks):
    return EventReport.objects.create(
        event=event,
        reporter=reporter,
        remarks=remarks,
    )


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_submit_event_report(request_data, user):
    _validate_event_report_request(request_data)
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    _validate_user_can_report_event(user, event)
    return _create_report(event, user, request_data.get('remarks'))


