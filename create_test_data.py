"""
Script to create test data for the multi-tenant e-commerce system.
Run: python manage.py shell < create_test_data.py
Or: python manage.py shell
     exec(open('create_test_data.py').read())
"""

from core.models import Tenant, User, Product, Order, OrderItem

print("Creating test data...")

# Create Tenant 1
tenant1, created = Tenant.objects.get_or_create(
    subdomain="techstore",
    defaults={
        'store_name': "Tech Store",
        'domain': "techstore.example.com",
        'contact_email': "admin@techstore.com",
        'contact_phone': "+1234567890"
    }
)
print(f"✓ Tenant 1: {tenant1.store_name} ({'created' if created else 'already exists'})")

# Create Tenant 2
tenant2, created = Tenant.objects.get_or_create(
    subdomain="fashionhub",
    defaults={
        'store_name': "Fashion Hub",
        'domain': "fashionhub.example.com",
        'contact_email': "admin@fashionhub.com",
        'contact_phone': "+9876543210"
    }
)
print(f"✓ Tenant 2: {tenant2.store_name} ({'created' if created else 'already exists'})")

# Create users for Tenant 1
owner1, created = User.objects.get_or_create(
    username="techstore_owner",
    defaults={
        'email': "owner@techstore.com",
        'tenant': tenant1,
        'role': User.Role.STORE_OWNER,
        'first_name': 'John',
        'last_name': 'Tech'
    }
)
if created:
    owner1.set_password("password123")
    owner1.save()
print(f"✓ Tech Store Owner: {owner1.username} ({'created' if created else 'already exists'})")

staff1, created = User.objects.get_or_create(
    username="techstore_staff",
    defaults={
        'email': "staff@techstore.com",
        'tenant': tenant1,
        'role': User.Role.STAFF,
        'first_name': 'Jane',
        'last_name': 'Assistant'
    }
)
if created:
    staff1.set_password("password123")
    staff1.save()
print(f"✓ Tech Store Staff: {staff1.username} ({'created' if created else 'already exists'})")

customer1, created = User.objects.get_or_create(
    username="techstore_customer",
    defaults={
        'email': "customer@example.com",
        'tenant': tenant1,
        'role': User.Role.CUSTOMER,
        'first_name': 'Alice',
        'last_name': 'Smith'
    }
)
if created:
    customer1.set_password("password123")
    customer1.save()
print(f"✓ Tech Store Customer: {customer1.username} ({'created' if created else 'already exists'})")

# Create users for Tenant 2
owner2, created = User.objects.get_or_create(
    username="fashion_owner",
    defaults={
        'email': "owner@fashionhub.com",
        'tenant': tenant2,
        'role': User.Role.STORE_OWNER,
        'first_name': 'Emma',
        'last_name': 'Fashion'
    }
)
if created:
    owner2.set_password("password123")
    owner2.save()
print(f"✓ Fashion Hub Owner: {owner2.username} ({'created' if created else 'already exists'})")

customer2, created = User.objects.get_or_create(
    username="fashion_customer",
    defaults={
        'email': "customer2@example.com",
        'tenant': tenant2,
        'role': User.Role.CUSTOMER,
        'first_name': 'Bob',
        'last_name': 'Jones'
    }
)
if created:
    customer2.set_password("password123")
    customer2.save()
print(f"✓ Fashion Hub Customer: {customer2.username} ({'created' if created else 'already exists'})")

# Create products for Tenant 1 (Tech Store)
products_tenant1 = [
    {
        'name': 'Wireless Mouse',
        'description': 'Ergonomic wireless mouse with 2.4GHz connectivity',
        'price': '29.99',
        'stock_quantity': 100,
        'sku': 'TECH-MOUSE-001'
    },
    {
        'name': 'Mechanical Keyboard',
        'description': 'RGB mechanical keyboard with blue switches',
        'price': '89.99',
        'stock_quantity': 50,
        'sku': 'TECH-KB-001'
    },
    {
        'name': 'USB-C Cable',
        'description': '2-meter braided USB-C cable',
        'price': '15.99',
        'stock_quantity': 200,
        'sku': 'TECH-CABLE-001'
    }
]

for product_data in products_tenant1:
    product, created = Product.objects.get_or_create(
        tenant=tenant1,
        sku=product_data['sku'],
        defaults={
            **product_data,
            'created_by': owner1
        }
    )
    if created:
        print(f"  ✓ Product: {product.name}")

# Create products for Tenant 2 (Fashion Hub)
products_tenant2 = [
    {
        'name': 'Cotton T-Shirt',
        'description': '100% organic cotton t-shirt',
        'price': '24.99',
        'stock_quantity': 150,
        'sku': 'FASH-TSHIRT-001'
    },
    {
        'name': 'Denim Jeans',
        'description': 'Slim fit denim jeans',
        'price': '59.99',
        'stock_quantity': 75,
        'sku': 'FASH-JEANS-001'
    },
    {
        'name': 'Leather Belt',
        'description': 'Genuine leather belt',
        'price': '34.99',
        'stock_quantity': 100,
        'sku': 'FASH-BELT-001'
    }
]

for product_data in products_tenant2:
    product, created = Product.objects.get_or_create(
        tenant=tenant2,
        sku=product_data['sku'],
        defaults={
            **product_data,
            'created_by': owner2
        }
    )
    if created:
        print(f"  ✓ Product: {product.name}")

print("\n✓ Test data creation complete!")
print("\nTest Credentials:")
print("=" * 50)
print("\nTenant 1 - Tech Store:")
print("  Owner:    techstore_owner / password123")
print("  Staff:    techstore_staff / password123")
print("  Customer: techstore_customer / password123")
print("\nTenant 2 - Fashion Hub:")
print("  Owner:    fashion_owner / password123")
print("  Customer: fashion_customer / password123")
print("\nAll users can login at: http://localhost:8000/api/auth/login/")
