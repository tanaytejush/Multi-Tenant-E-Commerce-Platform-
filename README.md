# Multi-Tenant E-commerce Backend

A multi-tenant e-commerce backend built with Django and Django REST Framework. Supports JWT authentication, role-based access control, and keeps each tenant's data completely separate.

## Features

- **Multi-Tenancy**: Multiple vendors can host their stores on a shared platform with complete data isolation
- **JWT Authentication**: Secure authentication with custom claims (tenant_id, role)
- **Role-Based Access Control**: Three user roles with different permissions:
  - **Store Owner**: Full access to all tenant data
  - **Staff**: Manage orders and products
  - **Customer**: View products and place orders
- **RESTful APIs**: Complete CRUD operations for Products and Orders
- **Tenant Isolation**: All data is automatically filtered by tenant
- **Admin Interface**: Django admin for easy management

## Technology Stack

- **Python 3.x**
- **Django 6.0**
- **Django REST Framework 3.16**
- **djangorestframework-simplejwt 5.5** - JWT authentication
- **django-cors-headers 4.9** - CORS support
- **SQLite** (default, easily configurable for PostgreSQL/MySQL)

## Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started quickly with pre-configured test data
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Detailed implementation guide and architecture

## Project Structure

```
multitenant_ecommerce/
├── core/                          # Main application
│   ├── migrations/                # Database migrations
│   ├── admin.py                   # Admin interface configuration
│   ├── models.py                  # Database models (Tenant, User, Product, Order, OrderItem)
│   ├── serializers.py             # DRF serializers
│   ├── views.py                   # API views
│   ├── permissions.py             # Custom permission classes
│   ├── middleware.py              # Tenant middleware
│   └── urls.py                    # API URL routing
├── multitenant_ecommerce/         # Project settings
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Root URL configuration
│   └── wsgi.py                    # WSGI configuration
├── docs/                          # Documentation
│   ├── QUICK_START.md             # Quick start guide
│   └── IMPLEMENTATION_SUMMARY.md  # Implementation details
├── scripts/                       # Utility scripts
│   ├── create_test_data.py        # Create sample test data
│   └── test_api.py                # API testing script
├── manage.py                      # Django management script (MUST be in root)
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables
├── .env.example                   # Example environment variables
└── README.md                      # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)

### 2. Clone the Repository

```bash
git clone <repository-url>
cd multitenant_ecommerce
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Environment Configuration

Create a `.env` file in the project root (or copy from `.env.example`):

```bash
cp .env.example .env
```

Update the `.env` file with your configuration:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register a new user | No |
| POST | `/api/auth/login/` | Login and get JWT tokens | No |
| POST | `/api/auth/refresh/` | Refresh access token | No |

### Products

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/api/products/` | List all products | Yes | All |
| POST | `/api/products/` | Create a new product | Yes | Store Owner |
| GET | `/api/products/{id}/` | Get product details | Yes | All |
| PUT | `/api/products/{id}/` | Update a product | Yes | Store Owner, Staff |
| PATCH | `/api/products/{id}/` | Partial update | Yes | Store Owner, Staff |
| DELETE | `/api/products/{id}/` | Delete a product | Yes | Store Owner |

**Query Parameters:**
- `search` - Search products by name, description, or SKU

### Orders

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/api/orders/` | List all orders | Yes | Store Owner, Staff |
| POST | `/api/orders/` | Create a new order | Yes | Customer |
| GET | `/api/orders/{id}/` | Get order details | Yes | All (filtered by permission) |
| PUT | `/api/orders/{id}/` | Update an order | Yes | Store Owner |
| PATCH | `/api/orders/{id}/` | Partial update | Yes | Store Owner |
| DELETE | `/api/orders/{id}/` | Delete an order | Yes | Store Owner |
| GET | `/api/orders/my_orders/` | Get current customer's orders | Yes | Customer |
| POST | `/api/orders/{id}/update_status/` | Update order status | Yes | Store Owner, Staff |

**Query Parameters:**
- `status` - Filter orders by status (PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED)

### Tenants

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/api/tenants/` | List tenants | Yes | Store Owner |
| GET | `/api/tenants/{id}/` | Get tenant details | Yes | Store Owner |

## API Usage Examples

### 1. Register a User

First, you need to create a tenant directly in the database or via Django admin.

**Request:**
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john_customer",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "tenant": 1,
  "role": "CUSTOMER",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_customer",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "tenant": 1,
  "role": "CUSTOMER",
  "phone": "+1234567890"
}
```

### 2. Login

**Request:**
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "john_customer",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_customer",
    "email": "john@example.com",
    "tenant_id": 1,
    "tenant_name": "Tech Store",
    "role": "CUSTOMER"
  }
}
```

### 3. Create a Product (Store Owner)

**Request:**
```bash
POST /api/products/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse with 2.4GHz connectivity",
  "price": "29.99",
  "stock_quantity": 100,
  "sku": "MOUSE-001",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "tenant": 1,
  "tenant_name": "Tech Store",
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse with 2.4GHz connectivity",
  "price": "29.99",
  "stock_quantity": 100,
  "sku": "MOUSE-001",
  "is_active": true,
  "created_by": 2,
  "created_by_username": "store_owner",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 4. List Products (Customer)

**Request:**
```bash
GET /api/products/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tenant": 1,
      "tenant_name": "Tech Store",
      "name": "Wireless Mouse",
      "description": "Ergonomic wireless mouse with 2.4GHz connectivity",
      "price": "29.99",
      "stock_quantity": 100,
      "sku": "MOUSE-001",
      "is_active": true,
      "created_by": 2,
      "created_by_username": "store_owner",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 5. Create an Order (Customer)

**Request:**
```bash
POST /api/orders/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "shipping_address": "123 Main St, New York, NY 10001",
  "notes": "Please deliver between 9 AM - 5 PM",
  "items": [
    {
      "product": 1,
      "quantity": 2
    },
    {
      "product": 2,
      "quantity": 1
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "tenant": 1,
  "tenant_name": "Tech Store",
  "customer": 1,
  "customer_username": "john_customer",
  "order_number": "ORD-A1B2C3D4",
  "status": "PENDING",
  "total_amount": "89.97",
  "shipping_address": "123 Main St, New York, NY 10001",
  "notes": "Please deliver between 9 AM - 5 PM",
  "items": [
    {
      "id": 1,
      "product": 1,
      "product_name": "Wireless Mouse",
      "product_sku": "MOUSE-001",
      "quantity": 2,
      "price_at_order": "29.99",
      "subtotal": "59.98"
    },
    {
      "id": 2,
      "product": 2,
      "product_name": "USB Cable",
      "product_sku": "CABLE-001",
      "quantity": 1,
      "price_at_order": "29.99",
      "subtotal": "29.99"
    }
  ],
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### 6. Update Order Status (Store Owner/Staff)

**Request:**
```bash
POST /api/orders/1/update_status/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "CONFIRMED"
}
```

**Response:**
```json
{
  "id": 1,
  "order_number": "ORD-A1B2C3D4",
  "status": "CONFIRMED",
  "total_amount": "89.97",
  ...
}
```

## Multi-Tenancy Implementation

### How It Works

I went with a shared database approach where all tenants use the same database and tables, but their data is kept separate using a `tenant` foreign key. It's simpler to manage than having separate databases for each tenant.

### Main Components

**Tenant Model**
The Tenant model stores basic vendor info like store name, domain, subdomain, and contact details. Each tenant is basically a separate vendor/store, and everything else (products, orders, users) links back to it.

**User Model**
Extended Django's default User model to add a `tenant` foreign key and a `role` field. There are three roles: Store Owner, Staff, and Customer.

**Tenant Middleware**
There's middleware in `core/middleware.py` that pulls the tenant_id and role from the JWT token on each request and attaches it to the request object. This way every request knows which tenant it belongs to.

**JWT Token Setup**
The JWT tokens include custom claims:
- `tenant_id` - which tenant the user belongs to
- `role` - what they can do (Store Owner, Staff, or Customer)
- Plus username and email

You can find this in `core/serializers.py` (look for `CustomTokenObtainPairSerializer`).

**Filtering Data**
All the ViewSets filter data by tenant automatically. For example:
```python
def get_queryset(self):
    user = self.request.user
    queryset = Product.objects.filter(tenant=user.tenant)
    return queryset
```

**Creating New Data**
When you create something new (like a product or order), the tenant is set automatically:
```python
def perform_create(self, serializer):
    serializer.save(
        tenant=self.request.user.tenant,
        created_by=self.request.user
    )
```

### Data Isolation

The data is isolated at multiple levels:
- Database queries are filtered by tenant automatically
- Permissions check that users can only access their own tenant's data
- New objects get assigned to the user's tenant
- JWT tokens include the tenant_id to prevent any cross-tenant access

## Role-Based Access Control

### How Permissions Work

There are custom permission classes in `core/permissions.py`:
- `IsTenantUser` - checks that the user belongs to a tenant
- `IsStoreOwner` - only allows store owners
- `IsStoreOwnerOrStaff` - allows both store owners and staff
- `TenantProductPermission` - handles product access based on role
- `TenantOrderPermission` - handles order access based on role

These permissions are applied to the ViewSets using `permission_classes`. They check permissions before any database queries run, at both the view level and object level.

The user's role is stored in the JWT token, so it's available on every request. The permission classes use this to decide what the user can and can't do.

### Permission Matrix

| Resource | Action | Store Owner | Staff | Customer |
|----------|--------|-------------|-------|----------|
| Products | List | ✓ (all) | ✓ (all) | ✓ (active only) |
| Products | Create | ✓ | ✗ | ✗ |
| Products | Read | ✓ | ✓ | ✓ (active only) |
| Products | Update | ✓ | ✓ | ✗ |
| Products | Delete | ✓ | ✗ | ✗ |
| Orders | List | ✓ (all) | ✓ (all) | ✓ (own only) |
| Orders | Create | ✓ | ✗ | ✓ |
| Orders | Read | ✓ (all) | ✓ (all) | ✓ (own only) |
| Orders | Update | ✓ | ✓ | ✗ |
| Orders | Delete | ✓ | ✗ | ✗ |
| Orders | Update Status | ✓ | ✓ | ✗ |

## Testing

### Create Test Data

Use the provided test data script for quick setup:

```bash
python manage.py shell < scripts/create_test_data.py
```

Or create test data manually using Django shell or admin interface:

```bash
python manage.py shell
```

```python
from core.models import Tenant, User

# Create a tenant
tenant = Tenant.objects.create(
    store_name="Tech Store",
    subdomain="techstore",
    contact_email="admin@techstore.com",
    contact_phone="+1234567890"
)

# Create a store owner
owner = User.objects.create_user(
    username="store_owner",
    password="password123",
    email="owner@techstore.com",
    tenant=tenant,
    role="STORE_OWNER"
)

# Create a customer
customer = User.objects.create_user(
    username="customer1",
    password="password123",
    email="customer@example.com",
    tenant=tenant,
    role="CUSTOMER"
)
```

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/`

Features:
- Manage tenants, users, products, orders
- Filter and search capabilities
- Inline order item management
- Custom user admin with tenant information

## Security Notes

A few things to keep in mind:

**Tokens**
- Access tokens expire after 1 hour
- Refresh tokens are valid for 7 days
- Always use HTTPS in production

**Passwords**
- Using Django's built-in password validation
- Passwords are hashed with PBKDF2

**CORS**
- Right now CORS is set to allow all origins for development
- In production, set `CORS_ALLOW_ALL_ORIGINS = False` and specify your actual frontend domain

**Environment Variables**
- Don't commit the `.env` file to git
- Use a strong SECRET_KEY in production (not the default one)

## Production Deployment

Before deploying to production, you'll want to:

- Set `DEBUG=False` in `.env`
- Switch to a proper database like PostgreSQL
- Use a strong SECRET_KEY
- Configure ALLOWED_HOSTS
- Set up static file serving
- Use HTTPS
- Fix CORS settings (don't use ALLOW_ALL in production)
- Add logging
- Use a production server like Gunicorn or uWSGI
- Set up a reverse proxy (Nginx)

## License

This project is provided for educational and evaluation purposes.

## Support

For issues, questions, or contributions, please contact the development team.
