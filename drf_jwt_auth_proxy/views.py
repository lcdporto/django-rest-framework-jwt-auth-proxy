import requests

from django.utils.translation import ugettext as _

from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions

from .settings import api_settings

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_remote_jwt_token(self, *args, **kwargs):
    """
    Receives credentials from user and pass them
    to the auth server
    """
    try:
        response = requests.post(api_settings.AUTH_SERVER, data=self.data)
        return Response(response.json())
    except requests.exceptions.ConnectionError:
        msg = _('Authentication server not available, please try again later.')
        raise exceptions.AuthenticationFailed(msg)
