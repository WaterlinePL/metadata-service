from flask_restful import Api, Resource

import logging
import config

from .src import metadata, status

api = Api(prefix=config.API_PREFIX)
logger = logging.getLogger()

class StatusAPI(Resource):
    def get(self, task_id):
        logger.log(msg=f'Task status',level=10)
        return status.check_status(task_id)

class MetadataAPI(Resource):
    def get(self):
        print(self)
        return 200

    def post(self):
        logger.log(msg="Process data",level=10)
        return metadata.process_files()



# data processing endpoint
api.add_resource(MetadataAPI, '/metadata')

# task status endpoint
api.add_resource(StatusAPI, '/status/<string:task_id>')
