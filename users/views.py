from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from djoser import email

from users.models import User
from users.serializers import UserListSerializer


# Create your views here.
class UserListAPIView(generics.ListAPIView):
    """Для получения объектов модели User."""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)


class ActivationEmail(email.ActivationEmail):
    """Для отправки сообщения после регистрации пользователя."""
    template_name = 'users/activation.html'


class PasswordResetEmail(email.PasswordResetEmail):
    """Для отправки сообщения, если пользователь решит сменить пароль."""
    template_name = 'users/password_reset_confirm.html'
