# FIX: import both urllib and requests does not make sense
# use requests of course
import jwt
from urllib import request
import requests

from django.contrib.auth import get_user_model
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File

from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)

from .settings import api_settings

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class BaseJSONWebTokenAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    """

    def gets(self, dic, fields):
        """
        Create a dict from an old dict using a list
        of fields, if the field does not exist this is going
        to blow up
        """
        return { k: dic[k] for k in fields }
    
    def get_remote_user_data(self):
        """
        Get remote user data from auth server
        """
        token = str(self.jwt_value, 'utf-8')
        headers = {"Authorization":"Bearer {0}".format(token)}
        try:
            data = requests.get(api_settings.AUTH_SERVER_USER_DATA, headers=headers).json()
            return data
        except requests.exceptions.ConnectionError:
            msg = _('Remote API not available, please try again later.')
            raise exceptions.AuthenticationFailed(msg)

    def get_remote_avatar(self, avatar):
        url = api_settings.AUTH_SERVER_MEDIA + avatar
        tmp = NamedTemporaryFile(delete=True)
        tmp.write(request.urlopen(url).read())
        tmp.flush()
        return File(tmp)
        
    def create_user_from_remote(self):
        """
        Create user from remote user data
        """
        # retrieve data
        data = self.get_remote_user_data()
        fields = api_settings.AUTH_SERVER_USER_FIELDS
        new_user_data = self.gets(data, fields)
        # this is a hack inside a hack, and should be temp
        new_user_data['avatar'] = self.get_remote_avatar(new_user_data['avatar'])
        # create user
        User = get_user_model()
        new_user = User.objects.create(**new_user_data)
        # make sure user password is unusable
        new_user.set_unusable_password()
        new_user.save()
        return new_user

        
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        
        if jwt_value is None:
            return None

        self.jwt_value = jwt_value
        
        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)

        return (user, jwt_value)

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            try:
                user = self.create_user_from_remote()
            except:
                msg = _('Invalid signature.')
                raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user


class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth or smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)