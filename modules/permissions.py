from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAndIsOwner(BasePermission):
    """
    Доступ разрешен только аутентифицированным пользователям. Детали записей могут смотреть только владельцы записей.
    Пользователь может видеть список всех модулей без возможности их как-то редактировать или удалять, если он не
    является их владельцем.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if request.user == obj.module_user:
                return True
        elif request.method in ('PATCH', 'PUT', 'POST'):
            return request.user == obj.module_user
        elif request.method == 'DELETE':
            if not request.user.is_authenticated:
                return False
            return request.user == obj.module_user or request.user.is_superuser
        return False
