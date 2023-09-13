from .exceptions import UnauthorizedException
from datetime import datetime
from django.http import HttpResponse
import mimetypes
import uuid


def get_id_token_from_authorization_header(authorization_header):
    try:
        return authorization_header.split()[1]

    except AttributeError:
        raise UnauthorizedException('No token was provided')

    except IndexError:
        raise UnauthorizedException('Given token is invalid')


def text_length_is_valid(text: str, min_value: int, max_value: int):
    return min_value <= len(text) <= max_value


def trim_all_request_attributes(request_attribute):
    if isinstance(request_attribute, str):
        return request_attribute.strip()

    elif isinstance(request_attribute, list):
        for value_index in range(len(request_attribute)):
            request_attribute[value_index] = trim_all_request_attributes(request_attribute[value_index])

        return request_attribute

    elif isinstance(request_attribute, dict):
        for key, value in request_attribute.items():
            request_attribute[key] = trim_all_request_attributes(value)

        return request_attribute

    else:
        return request_attribute


def get_date_from_date_time_string(iso_datetime):
    iso_datetime = iso_datetime.strip('Z')
    try:
        datetime_: datetime = datetime.fromisoformat(iso_datetime)
        return datetime_
    except ValueError:
        raise ValueError(f'{iso_datetime} is not a valid ISO date string')


def get_iso_date_time_from_date_time(date_time):
    return date_time.isoformat()


def is_valid_iso_date_string(iso_datetime):
    try:
        get_date_from_date_time_string(iso_datetime)
        return True
    except ValueError:
        return False


def is_valid_uuid_string(uuid_string):
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def get_prefix_from_file_name(file_name):
    try:
        prefix = file_name.split('.')[1]
        return prefix
    except IndexError:
        raise ValueError(f'{file_name} is not a proper file name')


def generate_file_response(response_file):
    content_type = mimetypes.guess_type(response_file.name)[0]
    file_response = HttpResponse(response_file, content_type=content_type)
    file_response['Content-Length'] = response_file.size
    file_response['Content-Disposition'] = f'attachment; filename="{response_file.name}"'
    file_response['Access-Control-Expose-Headers'] = 'Content-Disposition'
    return file_response
