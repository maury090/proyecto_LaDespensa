from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameBackend(BaseBackend):
    """
    Autenticador personalizado que permite iniciar sesión con:
    - Email
    - Username
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Verificar si se proporcionaron credenciales
        if username is None or password is None:
            return None

        # Intentar buscar el usuario por email o por username
        try:
            # Buscar por email (si el username parece un email)
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                # Buscar por username
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Si no se encuentra por email, intentar por username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        # Verificar la contraseña
        if user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None