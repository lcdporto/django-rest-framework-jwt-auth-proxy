import requests

from django.utils.translation import ugettext as _

from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions

from .settings import api_settings

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token_from_auth_server(self, *args, **kwargs):
    """
    Receives credentials from client and pass them to the auth server,
    receiving a jwt token or raising an exception if it is impossible
    to connect
    """
    try:
        response = requests.post(api_settings.AUTH_SERVER + api_settings.AUTH_SERVER_TOKEN_ENDPOINT, data=self.data)
        return Response(response.json())
    except requests.exceptions.ConnectionError:
        msg = _('Authentication server not available, please try again later.')
        raise exceptions.AuthenticationFailed(msg)
