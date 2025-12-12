from rest_framework import permissions
from .models import User


class IsTenantUser(permissions.BasePermission):
    """
    Permission to check if user belongs to the same tenant as the resource.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.tenant is not None

    def has_object_permission(self, request, view, obj):
        # Check if the object has a tenant attribute
        if hasattr(obj, 'tenant'):
            return obj.tenant == request.user.tenant
        return False


class IsStoreOwner(permissions.BasePermission):
    """
    Permission to check if user is a store owner.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.STORE_OWNER
        )


class IsStoreOwnerOrStaff(permissions.BasePermission):
    """
    Permission to check if user is a store owner or staff.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [User.Role.STORE_OWNER, User.Role.STAFF]
        )


class IsCustomer(permissions.BasePermission):
    """
    Permission to check if user is a customer.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.CUSTOMER
        )


class TenantProductPermission(permissions.BasePermission):
    """
    Custom permission for Product operations based on role.
    - Store Owner: Full CRUD access to tenant's products
    - Staff: Read, Update access to tenant's products
    - Customer: Read-only access to active products
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role == User.Role.STORE_OWNER:
            return True

        if request.user.role == User.Role.STAFF:
            return request.method in ['GET', 'PUT', 'PATCH']

        if request.user.role == User.Role.CUSTOMER:
            return request.method in permissions.SAFE_METHODS

        return False

    def has_object_permission(self, request, view, obj):
        # Ensure object belongs to same tenant
        if obj.tenant != request.user.tenant:
            return False

        if request.user.role == User.Role.STORE_OWNER:
            return True

        if request.user.role == User.Role.STAFF:
            return request.method in ['GET', 'PUT', 'PATCH']

        if request.user.role == User.Role.CUSTOMER:
            return request.method in permissions.SAFE_METHODS and obj.is_active

        return False


class TenantOrderPermission(permissions.BasePermission):
    """
    Custom permission for Order operations based on role.
    - Store Owner: Full access to all tenant orders
    - Staff: Can view and update orders
    - Customer: Can create and view only their own orders
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.STORE_OWNER, User.Role.STAFF]:
            return True

        if request.user.role == User.Role.CUSTOMER:
            return request.method in ['GET', 'POST']

        return False

    def has_object_permission(self, request, view, obj):
        # Ensure object belongs to same tenant
        if obj.tenant != request.user.tenant:
            return False

        if request.user.role == User.Role.STORE_OWNER:
            return True

        if request.user.role == User.Role.STAFF:
            return request.method in ['GET', 'PUT', 'PATCH']

        if request.user.role == User.Role.CUSTOMER:
            # Customers can only access their own orders
            return obj.customer == request.user

        return False
