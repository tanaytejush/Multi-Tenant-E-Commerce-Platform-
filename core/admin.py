from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Tenant, User, Product, Order, OrderItem


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'subdomain', 'contact_email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['store_name', 'subdomain', 'contact_email']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'tenant', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active', 'tenant']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Tenant Information', {'fields': ('tenant', 'role', 'phone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Tenant Information', {'fields': ('tenant', 'role', 'phone')}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'sku', 'price', 'stock_quantity', 'is_active', 'created_at']
    list_filter = ['tenant', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'tenant', 'customer', 'status', 'total_amount', 'created_at']
    list_filter = ['tenant', 'status', 'created_at']
    search_fields = ['order_number', 'customer__username', 'customer__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price_at_order', 'subtotal']
    search_fields = ['order__order_number', 'product__name']
    readonly_fields = ['subtotal']
