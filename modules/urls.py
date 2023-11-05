from django.urls import path

from modules.apps import ModulesConfig

from modules.views import ModuleCreateAPIView, ModuleListAPIView, ModuleRetrieveAPIView, ModuleUpdateAPIView, \
    ModuleDeleteAPIView

app_name = ModulesConfig.name

urlpatterns = [
    path('create/', ModuleCreateAPIView.as_view(), name='create_module'),
    path('', ModuleListAPIView.as_view(), name='list_module'),
    path('<int:pk>/', ModuleRetrieveAPIView.as_view(), name='detail_module'),
    path('update/<int:pk>/', ModuleUpdateAPIView.as_view(), name='update_module'),
    path('delete/<int:pk>/', ModuleDeleteAPIView.as_view(), name='delete_module')
]
