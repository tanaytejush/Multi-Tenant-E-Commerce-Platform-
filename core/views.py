from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q
import uuid

from .models import Tenant, User, Product, Order, OrderItem
from .serializers import (
    TenantSerializer, UserSerializer, RegisterSerializer,
    CustomTokenObtainPairSerializer, ProductSerializer,
    OrderSerializer, OrderListSerializer
)
from .permissions import (
    IsTenantUser, IsStoreOwner, IsStoreOwnerOrStaff,
    TenantProductPermission, TenantOrderPermission
)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Public endpoint - no authentication required.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view with tenant_id and role in token.
    """
    serializer_class = CustomTokenObtainPairSerializer


class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing tenants.
    Only store owners can view tenant information.
    """
    queryset = Tenant.objects.filter(is_active=True)
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, IsStoreOwner]

    def get_queryset(self):
        # Store owners can only see their own tenant
        if self.request.user.role == User.Role.STORE_OWNER:
            return Tenant.objects.filter(id=self.request.user.tenant.id)
        return Tenant.objects.none()


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Product CRUD operations.
    - Store Owner: Full CRUD access
    - Staff: Read and Update access
    - Customer: Read-only access to active products
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsTenantUser, TenantProductPermission]

    def get_queryset(self):
        user = self.request.user
        if not user.tenant:
            return Product.objects.none()

        queryset = Product.objects.filter(tenant=user.tenant)

        # Customers can only see active products
        if user.role == User.Role.CUSTOMER:
            queryset = queryset.filter(is_active=True)

        # Filter by search query if provided
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(sku__icontains=search)
            )

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        # Automatically set tenant and created_by
        serializer.save(
            tenant=self.request.user.tenant,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        # Ensure tenant doesn't change
        serializer.save(tenant=self.request.user.tenant)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Order CRUD operations.
    - Store Owner: Full access to all tenant orders
    - Staff: View and update orders
    - Customer: Create and view only their own orders
    """
    permission_classes = [IsAuthenticated, IsTenantUser, TenantOrderPermission]

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.tenant:
            return Order.objects.none()

        queryset = Order.objects.filter(tenant=user.tenant)

        # Customers can only see their own orders
        if user.role == User.Role.CUSTOMER:
            queryset = queryset.filter(customer=user)

        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('customer', 'tenant').prefetch_related('items').order_by('-created_at')

    def perform_create(self, serializer):
        # Generate unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        # Automatically set tenant and customer
        serializer.save(
            tenant=self.request.user.tenant,
            customer=self.request.user,
            order_number=order_number
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsStoreOwnerOrStaff])
    def update_status(self, request, pk=None):
        """
        Custom action to update order status.
        Only Store Owner and Staff can update status.
        """
        order = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Order.Status.choices):
            return Response(
                {'error': 'Invalid status value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """
        Get orders for the current customer.
        """
        if request.user.role != User.Role.CUSTOMER:
            return Response(
                {'error': 'This endpoint is only for customers'},
                status=status.HTTP_403_FORBIDDEN
            )

        orders = self.get_queryset().filter(customer=request.user)
        page = self.paginate_queryset(orders)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
