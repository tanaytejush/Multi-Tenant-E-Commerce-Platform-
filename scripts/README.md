# Utility Scripts

This directory contains utility scripts for testing and development.

## Available Scripts

### create_test_data.py
Creates sample test data including tenants, users, and products for development/testing.

**Usage:**
```bash
python manage.py shell < scripts/create_test_data.py
```

This creates:
- 2 test tenants (Tech Store and Fashion Hub)
- Multiple user accounts with different roles
- Sample products for each tenant

### test_api.py
Tests the API endpoints with pre-configured test data.

**Usage:**
```bash
python scripts/test_api.py
```

**Prerequisites:**
- Server must be running (`python manage.py runserver`)
- Test data must be created first (using `create_test_data.py`)
