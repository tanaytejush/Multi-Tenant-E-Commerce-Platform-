# Multi-Tenant E-commerce Backend

A robust multi-tenant e-commerce backend built with Django and Django REST Framework, featuring JWT authentication, role-based access control, and complete tenant isolation.

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
├── manage.py                      # Django management script
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

### Architecture Overview

The multi-tenancy implementation uses a **shared database with row-level isolation** approach. This means all tenants share the same database and tables, but data is isolated using a `tenant` foreign key.

### Key Components

#### 1. Tenant Model
- Stores vendor information (store_name, domain, subdomain, contact details)
- Each tenant represents a separate vendor/store
- All business data (products, orders, users) references a tenant

#### 2. Custom User Model
- Extends Django's `AbstractUser`
- Includes `tenant` foreign key and `role` field
- Three roles: STORE_OWNER, STAFF, CUSTOMER

#### 3. Tenant Middleware (`core/middleware.py`)
- Extracts `tenant_id` and `role` from JWT token
- Attaches them to the request object
- Makes every request tenant-aware

#### 4. Custom JWT Serializer
- Adds custom claims to JWT token:
  - `tenant_id`: Identifies which tenant the user belongs to
  - `role`: User's role (STORE_OWNER, STAFF, CUSTOMER)
  - `username`, `email`: Additional user info
- Located in `core/serializers.py` (`CustomTokenObtainPairSerializer`)

#### 5. Tenant-Aware Querysets
All ViewSets automatically filter data by tenant:
```python
def get_queryset(self):
    user = self.request.user
    queryset = Product.objects.filter(tenant=user.tenant)
    return queryset
```

#### 6. Automatic Tenant Assignment
When creating new objects, the tenant is automatically set:
```python
def perform_create(self, serializer):
    serializer.save(
        tenant=self.request.user.tenant,
        created_by=self.request.user
    )
```

### Data Isolation Guarantees

1. **Query-Level Isolation**: All database queries are automatically filtered by tenant
2. **Permission-Level Isolation**: Custom permissions ensure users can only access their tenant's data
3. **Creation-Level Isolation**: New objects are automatically assigned to the user's tenant
4. **Token-Level Isolation**: JWT tokens include tenant_id, preventing cross-tenant access

## Role-Based Access Control

### Implementation

Role-based access is implemented through:

1. **Custom Permission Classes** (`core/permissions.py`):
   - `IsTenantUser`: Ensures user belongs to a tenant
   - `IsStoreOwner`: Only store owners
   - `IsStoreOwnerOrStaff`: Store owners and staff
   - `TenantProductPermission`: Role-specific product access
   - `TenantOrderPermission`: Role-specific order access

2. **View-Level Permissions**:
   - Applied as `permission_classes` on ViewSets
   - Evaluated before any query execution
   - Provide both object-level and view-level checks

3. **JWT Token Claims**:
   - Role is embedded in JWT token
   - Available on every authenticated request
   - Used by permission classes to make decisions

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

You can create test data using Django shell or admin interface:

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

## Security Considerations

1. **JWT Token Security**:
   - Tokens expire after 1 hour
   - Refresh tokens valid for 7 days
   - Use HTTPS in production

2. **Password Security**:
   - Django's password validation enabled
   - Passwords hashed using PBKDF2

3. **CORS**:
   - Configure `CORS_ALLOW_ALL_ORIGINS = False` in production
   - Specify allowed origins

4. **Environment Variables**:
   - Never commit `.env` file
   - Use strong SECRET_KEY in production

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure proper database (PostgreSQL recommended)
3. Set up proper SECRET_KEY
4. Configure ALLOWED_HOSTS
5. Set up static file serving
6. Use HTTPS
7. Configure CORS properly
8. Set up proper logging
9. Use production-grade server (Gunicorn, uWSGI)
10. Set up reverse proxy (Nginx)

## License

This project is provided for educational and evaluation purposes.

## Support

For issues, questions, or contributions, please contact the development team.
