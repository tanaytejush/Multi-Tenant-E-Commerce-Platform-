from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import Tenant, User, Product, Order, OrderItem


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'store_name', 'domain', 'subdomain', 'contact_email', 'contact_phone', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.store_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'tenant', 'tenant_name', 'role', 'phone', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    tenant = serializers.PrimaryKeyRelatedField(queryset=Tenant.objects.filter(is_active=True))

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name', 'tenant', 'role', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['tenant_id'] = user.tenant.id if user.tenant else None
        token['role'] = user.role
        token['username'] = user.username
        token['email'] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add extra user info to response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'tenant_id': self.user.tenant.id if self.user.tenant else None,
            'tenant_name': self.user.tenant.store_name if self.user.tenant else None,
            'role': self.user.role,
        }

        return data


class ProductSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    tenant_name = serializers.CharField(source='tenant.store_name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'tenant', 'tenant_name', 'name', 'description', 'price', 'stock_quantity',
                  'sku', 'is_active', 'created_by', 'created_by_username', 'created_at', 'updated_at']
        read_only_fields = ['id', 'tenant', 'created_by', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_sku', 'quantity', 'price_at_order', 'subtotal']
        read_only_fields = ['id', 'price_at_order', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=False)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    tenant_name = serializers.CharField(source='tenant.store_name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'tenant', 'tenant_name', 'customer', 'customer_username', 'order_number',
                  'status', 'total_amount', 'shipping_address', 'notes', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'tenant', 'customer', 'order_number', 'total_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        total = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # Check stock availability
            if product.stock_quantity < quantity:
                raise serializers.ValidationError(f"Insufficient stock for {product.name}")

            # Create order item
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_order=product.price
            )

            # Update product stock
            product.stock_quantity -= quantity
            product.save()

            total += order_item.subtotal

        # Update order total
        order.total_amount = total
        order.save()

        return order

    def update(self, instance, validated_data):
        # Don't allow updating items through this serializer
        validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class OrderListSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    tenant_name = serializers.CharField(source='tenant.store_name', read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'tenant_name', 'customer_username', 'order_number', 'status',
                  'total_amount', 'items_count', 'created_at']
        read_only_fields = fields
