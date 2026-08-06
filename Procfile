web: gunicorn paysplit_core.wsgi:application
worker: celery -A paysplit_core worker --loglevel=info