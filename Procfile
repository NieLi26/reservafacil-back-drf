web: python manage.py migrate && gunicorn django_project.wsgi
web: python manage.py crontab add
celery: celery -A django_project worker -l INFO --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo
<!-- web: python manage.py tailwind build -->



