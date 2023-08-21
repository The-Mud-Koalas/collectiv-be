from communalspace.exceptions import InvalidRequestException


def _validate_update_user_data_request(request_data):
    """
    Check if full name is string, with length more than 3 and less than 50, and is not null
    Check if preferred radius is a positive integer
    Check if location-track is a boolean
    """
    if not request_data.get('full-name'):
        raise InvalidRequestException('Full name must not be null')

    if not isinstance(request_data.get('full-name'), str):
        raise InvalidRequestException('Full name must be a string')

    if not (3 <= len(request_data.get('full-name')) <= 50):
        raise InvalidRequestException('Full name must have a minimum length of 3 and a maximum length of 50')

    if not isinstance(request_data.get('preferred-radius'), int):
        raise InvalidRequestException('Preferred radius must be an integer')

    if request_data.get('preferred-radius') <= 0:
        raise InvalidRequestException('Preferred radius must be a positive integer')

    if not isinstance(request_data.get('location-track'), bool):
        raise InvalidRequestException('Location tracking preference must be a boolean')


def _update_user_data(user, request_data):
    user.set_full_name(request_data.get('full-name'))
    user.set_preferred_radius(request_data.get('preferred-radius'))
    user.set_location_track(request_data.get('location-track'))


def handle_update_user_data(user, request_data):
    _validate_update_user_data_request(request_data)
    _update_user_data(user, request_data)



