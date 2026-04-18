from rest_framework import permissions


def usuario_tiene_algun_rol(usuario, roles_permitidos):
    """
    Verifica si el usuario pertenece a alguno de los grupos permitidos.

    """
    if not usuario or not usuario.is_authenticated:
        return False

    if usuario.is_superuser:
        return True

    if not roles_permitidos:
        return False

    return usuario.groups.filter(name__in=roles_permitidos).exists()


class EstaAutenticadoLecturaORolEscritura(permissions.BasePermission):
    """
    Permiso general para ViewSets CRUD.

    """

    message = "No tiene permisos suficientes para realizar esta acción."

    def has_permission(self, request, view):
        usuario = request.user

        if not usuario or not usuario.is_authenticated:
            return False

        if usuario.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        roles_escritura = getattr(view, "roles_escritura", [])
        return usuario_tiene_algun_rol(usuario, roles_escritura)


class EstaAutenticadoYConRol(permissions.BasePermission):
    """
    Permiso estricto para endpoints sensibles.

    """

    message = "No tiene permisos para acceder a este módulo."

    def has_permission(self, request, view):
        usuario = request.user
        roles_permitidos = getattr(view, "roles_permitidos", [])

        return usuario_tiene_algun_rol(usuario, roles_permitidos)