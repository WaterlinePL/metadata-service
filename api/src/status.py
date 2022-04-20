from tasks import celery
from flask import jsonify
import logging

logger = logging.getLogger()

def check_status(task_id: str) -> str:  
    task = celery.AsyncResult(task_id)
    logger.log(msg=f'{task_id}/{task.state}',level=10)
    return jsonify(task.state)