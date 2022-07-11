import time,os, stat
import zipfile
import json

from tasks import celery
from celery import states
from minio import Minio

import logging
import config

logger = logging.getLogger()

client = Minio(config.minio_url,
    access_key=config.minio_access_key,
    secret_key=config.minio_secret_key, 
    secure=False)

def get(bucket: str, filename: str) -> str:
    task = process_file.delay(bucket,filename)
    return {'task_id': task.id}, 200


@celery.task(bind=True)
def process_file(self, bucket, filename):
    print(f'Process file task {bucket} {filename}')
    local_file_path = f'/tmp/{filename}'
    # self.update_state(state=celery.states.FAILURE, meta="Reason")
    self.update_state(state=states.STARTED)
    try:
        client.fget_object(bucket, filename, local_file_path)
        # os.chmod(local_file_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        dictionary = {}
        if local_file_path.endswith('.zip'):
            zip_obj= zipfile.ZipFile(local_file_path,"r")
            content_list = zip_obj.namelist()
            dictionary["extension"] = "zip"
            dictionary["content_list"] = content_list
            os.remove(filename)
    except Exception as e:
        print(f'EXCEPTION in process_file task: {str(e)}')
        raise e
    return {'result':  dictionary} 

    