# E-commerce Website
E-commerce website in Django

LINK: https://djangoecommerce.me

## Getting started
### Requirements
 - Python 3.6+
 - PIP
 - venv
 - Redis

### Installation
```
# Clone the repository
git clone https://github.com/omganeshdahale/ecommerce.git

# Enter into the directory
cd ecommerce/

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Apply migrations.
python manage.py migrate

# Create groups
python manage.py create_groups
```
### Configuration
Create `.env` file in cwd and add the following
```
SECRET_KEY=''
DEBUG=True

EMAIL_USER=''
EMAIL_PASS=''

STRIPE_PUBLIC_KEY=''
STRIPE_SECRET_KEY=''
STRIPE_WEBHOOK_SECRET=''
```
```
# Create a superuser account (follow the prompts afterwards)
python manage.py createsuperuser
```
### Starting the application
```
python manage.py runserver
```
### Starting redis server
```
redis-server
```
### Starting celery worker
```
celery -A myproject worker --loglevel=INFO
```