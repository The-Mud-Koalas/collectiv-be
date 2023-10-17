from django.core.exceptions import ObjectDoesNotExist
from firebase_admin import auth, exceptions as firebase_exceptions


def get_user_id_from_email(email):
    try:
        return auth.get_user_by_email(email).uid

    except firebase_exceptions.InvalidArgumentError:
        raise ObjectDoesNotExist(f'User with email {email} does not exist')


def get_user_id_from_phone_number(phone_number):
    try:
        return auth.get_user_by_phone_number(phone_number).uid

    except firebase_exceptions.InvalidArgumentError:
        raise ObjectDoesNotExist(f'User with phone number {phone_number} does not exist')


def get_user_id_from_email_or_phone_number(email_or_phone_number):
    if '@' in email_or_phone_number:
        return get_user_id_from_email(email_or_phone_number)

    else:
        return get_user_id_from_phone_number(email_or_phone_number)


def get_email_or_phone_number_from_id(user_id):
    firebase_user = auth.get_user(user_id)
    return firebase_user.email if firebase_user.email is not None else firebase_user.phone_number


def get_email_from_id(user_id):
    firebase_user = auth.get_user(user_id)
    return firebase_user.email


def embed_emails_to_user_data(user_data):
    for user_datum in user_data:
        user_datum['email'] = get_email_from_id(user_datum.get('user_id'))

    return user_data

