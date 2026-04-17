"""
Sistema de permisos personalizados para el sistema de panadería.

Define roles de negocio y permisos por módulo según el documento operativo.
Roles implementados:
- Administrador: Acceso total a todos los módulos
- JefeProduccion: Acceso al módulo de Producción
- Vendedor: Acceso al módulo de Ventas
- Bodeguero: Acceso al módulo de Bodega
"""

from rest_framework import permissions
from django.contrib.auth.models import Group


class BaseRolePermission(permissions.BasePermission):
    """Permiso base que verifica si el usuario pertenece a un grupo específico."""
    
    group_name = None
    message = "No tiene permisos suficientes para realizar esta acción."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return True
            
        if self.group_name is None:
            return False
            
        return request.user.groups.filter(name=self.group_name).exists()


class IsAdministrador(BaseRolePermission):
    """Permiso para usuarios con rol Administrador (acceso total)."""
    group_name = "Administrador"
    message = "Se requiere rol de Administrador para esta acción."


class IsJefeProduccion(BaseRolePermission):
    """Permiso para usuarios con rol Jefe de Producción."""
    group_name = "JefeProduccion"
    message = "Se requiere rol de Jefe de Producción para esta acción."


class IsVendedor(BaseRolePermission):
    """Permiso para usuarios con rol Vendedor."""
    group_name = "Vendedor"
    message = "Se requiere rol de Vendedor para esta acción."


class IsBodeguero(BaseRolePermission):
    """Permiso para usuarios con rol Bodeguero."""
    group_name = "Bodeguero"
    message = "Se requiere rol de Bodeguero para esta acción."


class ModulePermission(permissions.BasePermission):
    """
    Permiso por módulo que controla acceso basado en el rol del usuario.
    
    Mapeo de módulos a roles permitidos:
    - Producción: Administrador, JefeProduccion
    - Bodega: Administrador, Bodeguero
    - Ventas: Administrador, Vendedor
    - Catálogos base: Solo Administrador
    """
    
    MODULE_PERMISSIONS = {
        'catalogo': ['Administrador'],  # Turnos, Distribuciones, Tipos de Producción
        'produccion': ['Administrador', 'JefeProduccion'],
        'bodega': ['Administrador', 'Bodeguero'],
        'ventas': ['Administrador', 'Vendedor'],
        'reportes': ['Administrador', 'JefeProduccion', 'Vendedor', 'Bodeguero'],
    }
    
    def __init__(self, module):
        self.module = module
        self.message = f"No tiene permisos para acceder al módulo {module}."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return True
        
        # Obtener grupos del usuario
        user_groups = request.user.groups.values_list('name', flat=True)
        
        # Verificar si algún grupo del usuario tiene permiso para el módulo
        allowed_groups = self.MODULE_PERMISSIONS.get(self.module, [])
        return any(group in allowed_groups for group in user_groups)


# Permisos predefinidos por módulo para facilidad de uso
IsCatalogoOnly = lambda: ModulePermission('catalogo')
IsProduccionModule = lambda: ModulePermission('produccion')
IsBodegaModule = lambda: ModulePermission('bodega')
IsVentasModule = lambda: ModulePermission('ventas')
IsReportesModule = lambda: ModulePermission('reportes')


class WriteWithRolePermission(permissions.BasePermission):
    """
    Permiso que permite lectura a todos los autenticados, pero escritura solo con rol específico.
    
    Útil para endpoints que deben ser visibles pero no modificables por todos.
    """
    
    def __init__(self, write_roles):
        self.write_roles = write_roles
        self.message = f"Solo usuarios con roles {write_roles} pueden realizar operaciones de escritura."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return True
        
        # Operaciones de lectura permitidas para cualquier autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Para operaciones de escritura, verificar roles
        user_groups = request.user.groups.values_list('name', flat=True)
        return any(group in self.write_roles for group in user_groups)