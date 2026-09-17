import os
from celery import Celery  # Import Celery from the celery package, NOT your own module

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigstories.settings')  # Replace with your real Django settings module path

app = Celery('bigstories')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')