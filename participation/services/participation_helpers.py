from communalspace.exceptions import InvalidRequestException, RestrictedAccessException
from communalspace.settings import POINTS_PER_ATTENDANCE
from event.choices import EventType
from event.exceptions import InvalidCheckInCheckOutException
from event.models import AttendableEventParticipation


def validate_user_is_not_event_creator(event, user):
    if event.get_creator() == user:
        raise InvalidRequestException('Event creator cannot register/contribute through this action')


def validate_event_is_on_going(event):
    if not event.is_ongoing():
        raise InvalidRequestException('Event has not started or has been completed')


def validate_user_is_inside_event_location(event, user_latitude, user_longitude):
    if not event.check_user_is_inside_event(user_latitude, user_longitude):
        raise InvalidRequestException(f'User is currently not inside event location')


def validate_user_can_check_in(user, participation):
    if user.is_currently_attending_event() or participation.get_is_currently_attending():
        raise InvalidCheckInCheckOutException('User is currently attending an event')


def validate_user_is_attending_event(participation):
    if not participation.get_is_currently_attending():
        raise InvalidCheckInCheckOutException('User is currently not attending event')


def validate_user_is_a_volunteer(participation):
    if participation is None or participation.get_participation_type() != 'volunteer':
        raise InvalidRequestException('User is not a volunteer of event')


def validate_assisting_user_is_manager_of_event(event, assisting_user):
    if not event.check_user_can_act_as_manager(assisting_user):
        raise RestrictedAccessException(
            'Assisting user has not been granted manager access or is currently not checked in'
        )


def check_in_user(user, attendable_event, attendable_participation):
    check_in_data = attendable_participation.check_in()
    user.set_currently_attended_event(attendable_event)
    user.set_currently_attending_role(attendable_participation.get_participation_type())
    return check_in_data


def check_out_user(user, attendable_participation):
    check_out_data = attendable_participation.check_out()
    user.remove_currently_attended_event()
    return handle_reward_grant(user, check_out_data, attendable_participation)


def handle_reward_grant(user, activity_data, attendable_participation):
    reward_and_check_out_data = {**activity_data}
    if attendable_participation.is_eligible_for_reward():
        user.add_reward(POINTS_PER_ATTENDANCE)
        attendable_participation.set_rewarded(True)
        reward_and_check_out_data['is_rewarded'] = True

    else:
        reward_and_check_out_data['is_rewarded'] = False

    return reward_and_check_out_data


def validate_event_is_initiative(event):
    if event.get_type() != EventType.INITIATIVE:
        raise InvalidRequestException(f'Event with ID {event.get_id()} is not an initiative')


def force_check_out_participants_of_event(event):
    non_checked_out_participations = (AttendableEventParticipation.objects
                                      .filter_by_event(event)
                                      .filter(is_currently_attending=True))

    for participation in non_checked_out_participations:
        participant = participation.get_participant()
        participant.remove_currently_attended_event()
        participation.check_out()
        participation.set_violated_geofencing_rule()
