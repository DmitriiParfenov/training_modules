from rest_framework import serializers

from users.models import User


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'city', 'avatar')
        ref_name = 'UserListSerializer'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'city', 'phone', 'avatar')
        ref_name = 'UserSerializer'
