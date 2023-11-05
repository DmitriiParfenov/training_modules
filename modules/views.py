from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from modules.models import Module
from modules.permissions import IsAuthenticatedAndIsOwner
from modules.serializers import ModuleCreateSerializer, ModuleSerializer
from modules.tasks import send_email_creation


# Create your views here.
class ModuleCreateAPIView(generics.CreateAPIView):
    """Для создания объектов модели Module."""

    queryset = Module.objects.all()
    serializer_class = ModuleCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        new_mod = serializer.save()
        title = f'{new_mod.title}'

        # Запуск асинхронной задачи по отправке сообщения на указанный электронный адрес
        send_email_creation.delay(
            self.request.user.email, title
        )
        if not self.request.user.is_staff:
            new_mod.model_user = self.request.user
        new_mod.save()


class ModuleListAPIView(generics.ListAPIView):
    """Для просмотра информации об объектах модели Module."""

    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = (IsAuthenticatedAndIsOwner,)


class ModuleRetrieveAPIView(generics.RetrieveAPIView):
    """Для получения детальной информации об объекте модели Module."""

    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = (IsAuthenticatedAndIsOwner,)


class ModuleUpdateAPIView(generics.UpdateAPIView):
    """Для изменения объекта модели Module."""

    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = (IsAuthenticatedAndIsOwner,)


class ModuleDeleteAPIView(generics.DestroyAPIView):
    """Для удаления объектов модели Module."""

    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = (IsAuthenticatedAndIsOwner,)
