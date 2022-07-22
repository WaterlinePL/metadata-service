from flask import request
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
    def get(self):
        json_data = request.get_json(force=True)
        bucket = json_data['bucket']
        filename = json_data['filename']
        logger.log(msg=f'Get metadata for bucket {bucket} and file {filename}',level=10)
        return metadata.get(bucket,filename)

class MetadataDatahubAPI(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        urn = json_data['urn']
        logger.log(msg=f'Process metadata for urn {urn}',level=10)
        return metadata.process(urn)

class MetadataUnprocessedFileListApi(Resource):
    def get(self):
        request_query = 'hydrological-simulations'
        filtered_tag = "urn:li:tag:metadata-processed"
        logger.log(msg=f'List unprocessed files',level=10)
        return metadata.list_not_processed_files(request_query,filtered_tag)

# unprocessed files list endpoint
api.add_resource(MetadataUnprocessedFileListApi, '/unprocessed/')

# data processing endpoint
api.add_resource(MetadataAPI, '/get/')

# data processing endpoint
api.add_resource(MetadataDatahubAPI, '/process/')

# task status endpoint
api.add_resource(StatusAPI, '/status/<string:task_id>')
