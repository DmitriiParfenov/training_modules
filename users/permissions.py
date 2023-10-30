from rest_framework.permissions import BasePermission


class IsAuthenticatedOrIsOwner(BasePermission):
    """
    Доступ для безопасных методов разрешен только аутентифицированным пользователям. Расширенную информацию могут
    смотреть, а также ее обновлять, только владельцы записей.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.email == obj.email:
            return True
        return False
