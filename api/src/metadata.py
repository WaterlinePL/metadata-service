import time

from tasks import celery
from celery import states
def process_files():
    task = process_data.delay()
    return {'task_id': task.id}, 200


@celery.task(bind=True)
def process_data(self):
    # self.update_state(state=celery.states.FAILURE, meta="Reason")
    self.update_state(state=states.STARTED)
    time.sleep(20)
    