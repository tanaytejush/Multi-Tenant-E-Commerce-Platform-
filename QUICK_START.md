# Quick Start Guide

## Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd multitenant_ecommerce

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create test data (optional but recommended)
python manage.py shell < create_test_data.py
```

## 2. Run the Server

```bash
python manage.py runserver
```

Server will be available at: http://localhost:8000

## 3. Test the API

### Login as a Customer
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "techstore_customer",
    "password": "password123"
  }'
```

Copy the `access` token from the response.

### List Products
```bash
curl http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create an Order
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": "123 Main St, New York, NY 10001",
    "items": [
      {"product": 1, "quantity": 2}
    ]
  }'
```

## 4. Test Credentials

**Tech Store (Tenant 1):**
- Owner: `techstore_owner` / `password123`
- Staff: `techstore_staff` / `password123`
- Customer: `techstore_customer` / `password123`

**Fashion Hub (Tenant 2):**
- Owner: `fashion_owner` / `password123`
- Customer: `fashion_customer` / `password123`

## 5. Admin Interface

Create a superuser:
```bash
python manage.py createsuperuser
```

Access admin at: http://localhost:8000/admin/

## Key API Endpoints

- **Register**: POST `/api/auth/register/`
- **Login**: POST `/api/auth/login/`
- **Products**: GET/POST `/api/products/`
- **Orders**: GET/POST `/api/orders/`
- **My Orders**: GET `/api/orders/my_orders/`

For full API documentation, see [README.md](README.md)
