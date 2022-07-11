import time,os, stat
import zipfile
import pathlib

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
    task = get_file_metadata_task.delay(bucket,filename)
    return {'task_id': task.id}, 200

def process(bucket: str, filename: str) -> str:
    task = process_file_metadata_task.delay(bucket,filename)
    return {'task_id': task.id}, 200

@celery.task(bind=True)
def get_file_metadata_task(self, bucket, filename):
    print(f'Get file metadata task {bucket} {filename}')
    self.update_state(state=states.STARTED)
    try:
        dictionary = process_file(bucket, filename)
    except Exception as e:
        print(f'EXCEPTION in get_file_metadata task: {str(e)}')
        raise e
    return {'result':  dictionary} 

@celery.task(bind=True)
def process_file_metadata_task(self, bucket, filename):
    print(f'Process file task {bucket} {filename}')
    self.update_state(state=states.STARTED)
    try:
        dictionary = process_file(bucket, filename)
    except Exception as e:
        print(f'EXCEPTION in process_file task: {str(e)}')
        raise e
    return {'result':  dictionary} 

    
def process_file(bucket: str, filename: str) -> dict:
    dictionary = {}
    local_file_path = f'/tmp/{filename}'
    client.fget_object(bucket, filename, local_file_path)
    extension = pathlib.Path(filename).suffix
    dictionary["extension"] = extension

    if extension == '.zip':
        zip_obj= zipfile.ZipFile(local_file_path,"r")
        content_list = zip_obj.namelist()
        dictionary["content_list"] = content_list

    os.remove(local_file_path)
    return dictionary