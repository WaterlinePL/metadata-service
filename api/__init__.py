import time
from flask import jsonify
from flask_restful import Api, Resource

from tasks import celery
import logging
import config

api = Api(prefix=config.API_PREFIX)
logger = logging.getLogger()

class StatusAPI(Resource):
    def get(self, task_id):
        logger.log(msg=f'Task {task_id} status',level=10)
        task = celery.AsyncResult(task_id)
        return jsonify(task.state)

class MetadataAPI(Resource):
    def get(self):
        print(self)
        return 200

    def post(self):
        logger.log(msg="Process data",level=10)
        task = process_data.delay()
        return {'task_id': task.id}, 200

@celery.task()
def process_data(self):
    self.update_state(state='STARTED')
    time.sleep(60)

# data processing endpoint
api.add_resource(MetadataAPI, '/metadata')

# task status endpoint
api.add_resource(StatusAPI, '/status/<string:task_id>')
