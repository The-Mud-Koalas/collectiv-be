from communalspace.exceptions import InvalidRequestException
from users.services import utils as user_utils


def _validate_redeem_reward_request(request_data):
    if not isinstance(request_data.get('reward_point_cost'), int) or request_data.get('reward_point_cost') <= 0:
        raise InvalidRequestException('Reward point cost must be a positive integer')


def handle_redeem_reward(request_data, user):
    # Use additional filter to ensure that user is not modified by other transactions
    user = user_utils.get_user_by_id_or_raise_exception_thread_safe(user_id=user.get_user_id())
    _validate_redeem_reward_request(request_data)
    user.redeem_reward(request_data.get('reward_point_cost'))
    return {
        'amount_redeemed': request_data.get('reward_point_cost'),
        'user_new_points': user.get_reward_points()
    }

