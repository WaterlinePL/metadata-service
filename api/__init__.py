from flask_restful import Api, Resource

import logging
import config

from .src import metadata, status, minio_init

api = Api(prefix=config.API_PREFIX)
logger = logging.getLogger()

minio_init.init_buckets(['input-data','output-data'])

class StatusAPI(Resource):
    def get(self, task_id):
        logger.log(msg=f'Task status',level=10)
        return status.check_status(task_id)

class MetadataAPI(Resource):
    def get(self, bucket, filename):
        logger.log(msg=f'Get metadata for bucket {bucket} and file {filename}',level=10)
        return metadata.get(bucket,filename)

    def post(self, bucket, filename):
        logger.log(msg=f'Get metadata for bucket {bucket} and file {filename}',level=10)
        return metadata.get(bucket,filename)



# data processing endpoint
api.add_resource(MetadataAPI, '/process/<string:bucket>/<string:filename>/')

# task status endpoint
api.add_resource(StatusAPI, '/status/<string:task_id>')
