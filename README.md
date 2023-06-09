# darazscrape-api
Do the following to run \
python manage.py runserver \
sudo service redis-server start \
celery -A backend worker -l INFO \
celery -A backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
