from .services import reward
from communalspace.decorators import firebase_authenticated
from django.db import transaction
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_redeem_reward(request):
    """
    This view serves as the endpoint for user to redeem
    their points into reward. In the current implementation,
    this endpoint will only deduct the user's point without
    being integrated to any reward provider.
    -------------------------------------------------------
    request-body must contain:
    reward_point_cost: integer (the number of points to be deducted)
    """
    request_data = json.loads(request.body.decode('utf-8'))
    redeem_reward_data = reward.handle_redeem_reward(request_data, request.user)
    response_data = {
        'message': 'Reward was successfully redeemed',
        'point_data': redeem_reward_data
    }
    return Response(data=response_data)


