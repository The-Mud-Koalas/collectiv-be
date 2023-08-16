from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


@require_GET
@api_view(['GET'])
@permission_classes([])
def main(request):
    response_data = {
        'message': 'Hello, World!'
    }

    return Response(data=response_data)


