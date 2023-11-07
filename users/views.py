from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from users.models import User
from users.serializers import UserListSerializer


# Create your views here.
class UserListAPIView(generics.ListAPIView):
    """Для получения объектов модели User."""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)
