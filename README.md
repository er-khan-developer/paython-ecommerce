# My E-Commerce Platform

A Django-based e-commerce application with product catalog, shopping cart, orders, and user management features.

## Features

- User authentication and registration
- Product catalog with filtering
- Shopping cart management
- Order placement and tracking
- Two-factor authentication (2FA)
- Payment integration (Stripe)
- Order invoices
- Admin dashboard

## Project Structure

```
my_ecommerce/
├── manage.py                 # Django management script
├── requirements.txt          # Project dependencies
├── core/                     # Project settings and configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── users/                    # User management app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── login.py
│   └── urls.py
├── products/                 # Product catalog app
│   ├── models.py
│   ├── views.py
│   └── admin.py
├── carts/                    # Shopping cart app
│   ├── models.py
│   ├── views.py
│   ├── context_processors.py
│   └── urls.py
├── orders/                   # Order management app
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── templates/                # HTML templates
├── static/                   # Static files (CSS, JS)
├── media/                    # User-uploaded media
└── env/                      # Virtual environment
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd my_ecommerce
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/Scripts/activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=mysql://user:password@localhost/ecommerce_db
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

## Dependencies

See `requirements.txt` for all project dependencies. Main packages include:

- Django 6.1
- Pillow (image processing)
- Stripe (payment processing)
- pyotp (2FA)
- qrcode (QR code generation)
- mysqlclient (MySQL database)

## Usage

### Admin Panel

Access the Django admin panel at `/admin/` with your superuser credentials.

### User Features

- Sign up and login
- Browse products
- Add items to cart
- Place orders
- Set up 2FA
- View order history and invoices

## Database

The project uses MySQL as the default database. Update `DATABASES` in `core/settings.py` if using a different database.

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues or questions, please open an issue in the repository.
