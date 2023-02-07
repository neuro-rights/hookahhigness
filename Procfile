release: python manage.py migrate --noinput
web: gunicorn moralis_auth.wsgi --preload --timeout 1500 --keep-alive 5 --log-level debug