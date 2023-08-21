from .exceptions import UnauthorizedException


def get_id_token_from_authorization_header(authorization_header):
    try:
        return authorization_header.split()[1]

    except AttributeError:
        raise UnauthorizedException('No token was provided')

    except IndexError:
        raise UnauthorizedException('Given token is invalid')

