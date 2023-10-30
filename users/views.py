from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from users.models import User
from users.permissions import IsAuthenticatedOrIsOwner
from users.serializers import UserListSerializer, UserSerializer


# Create your views here.
class UserListAPIView(generics.ListAPIView):
    """Для получения объектов модели User."""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)


class UserUpdateAPIView(generics.UpdateAPIView):
    """Для изменения информации объектов модели User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrIsOwner,)


class UserDetailAPIView(generics.RetrieveAPIView):
    """Для получения детализированной информации объектов модели User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrIsOwner,)


class UserDeleteAPIview(generics.DestroyAPIView):
    """Для удаления объектов модели User."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
