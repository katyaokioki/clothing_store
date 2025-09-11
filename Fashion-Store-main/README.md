# Fashion Store (Django + DRF)

A full-stack e-commerce website for clothing & accessories.

## Features (All requirements covered)
- User Auth: signup, login (email), logout, password reset via email token
- Product CRUD with size/color variants, image, category
- Filters: category, size, color, price range + search & ordering
- Cart CRUD with variant quantities
- Orders CRUD with status management + tracking number
- Discount codes (coupons) applied at cart/order
- Responsive Bootstrap UI (home, product details, cart, orders, order detail)
- DRF APIs for everything (`/api/...`) with JWT auth
- Swagger docs at `/swagger/`
- Security: hashed passwords, CSRF, JWT for APIs, session auth for web
- Reviews & ratings API
- Outfit recommendations (simple: same category)

## Migrations Sequence (migrate app in this sequence)
1: accounts
2 :catalog
3: cart
4: orders

## Quickstart

```bash
python -m venv venv
source env/bin/activate  # on Windows: env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser --email admin@example.com
python manage.py runserver
```

Visit:
- Web UI: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Swagger: http://127.0.0.1:8000/swagger/

## API Auth (JWT)
- `POST /api/auth/signup/` {email, password, name?, phone?}
- `POST /api/auth/token/` {email, password}
- Use `Authorization: Bearer <access>` for subsequent API calls.

## Key API Endpoints
- Products: `/api/products/products/` (CRUD, filters), Variants `/api/products/variants/`, Categories `/api/products/categories/`
- Reviews: `/api/products/reviews/`
- Cart: `/api/cart/` (get/create), `/api/cart/items/` (CRUD)
- Orders: `/api/orders/` (CRUD, admin can see all), `/api/orders/create_from_cart/`
- Coupons: `/api/orders/coupons/` (admin only)

## Database
- MySQL is default. To use PostgreSQL set `DB_ENGINE=postgres` in `.env`.

## Email Reset
By default uses console backend. Configure SMTP in `.env` for real emails.

## Notes
This is a clean starting point; extend styling and business logic as needed.


