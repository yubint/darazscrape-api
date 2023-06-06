import os 

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-every-midnight':{
        'task':'api.tasks.update',
        'schedule':crontab(minute=0, hour= 0 ),
    }
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
