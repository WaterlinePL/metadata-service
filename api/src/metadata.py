import time, os
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

def get(bucket, filename):
    client.fget_object(bucket, filename, filename)
    dictionary = {}
    if filename.endswith('.zip'):
        zip_obj= zipfile.ZipFile(filename,"r")
        content_list = zip_obj.namelist()
        dictionary["extension"] = "zip"
        dictionary["content_list"] = content_list

    os.remove(filename)
    return {'metadata': json.dumps(dictionary, indent = 4) 
}

def process_files():
    task = process_data.delay()
    return {'task_id': task.id}, 200


@celery.task(bind=True)
def process_data(self):
    # self.update_state(state=celery.states.FAILURE, meta="Reason")
    self.update_state(state=states.STARTED)
    time.sleep(20)
    