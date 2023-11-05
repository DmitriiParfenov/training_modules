from rest_framework import serializers

from modules.models import Module
from modules.validators import TitleValidation
from users.models import User
from users.serializers import UserListSerializer


class ModuleCreateSerializer(serializers.ModelSerializer):
    module_user = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())

    class Meta:
        model = Module
        fields = ('id', 'title', 'description', 'module_user')
        validators = [TitleValidation(field='title')]


class ModuleSerializer(serializers.ModelSerializer):
    module_user = UserListSerializer(read_only=True)

    class Meta:
        model = Module
        fields = ('id', 'title', 'description', 'module_user')
        validators = [TitleValidation(field='title')]
