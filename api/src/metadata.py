import os
import zipfile
import pathlib
import requests, json
from tasks import celery
from celery import states
from minio import Minio

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.mce_builder import make_tag_urn
from datahub.emitter.rest_emitter import DatahubRestEmitter

from datahub.metadata.schema_classes import (
    ChangeTypeClass,
    GlobalTagsClass,
    TagAssociationClass,
    DatasetPropertiesClass
)


import logging
import config

logger = logging.getLogger()

client = Minio(config.minio_url,
    access_key=config.minio_access_key,
    secret_key=config.minio_secret_key, 
    secure=config.minio_secure)

def get(bucket: str, filename: str) -> str:
    task = get_file_metadata_task.delay(bucket,filename)
    return {'task_id': task.id}, 200

def process(urn: str) -> str:
    task = process_file_metadata_task.delay(urn)
    return {'task_id': task.id}, 200

@celery.task(bind=True)
def get_file_metadata_task(self, bucket, filename):
    print(f'Get file metadata task {bucket} {filename}')
    self.update_state(state=states.STARTED)
    try:
        dictionary, _ = process_file(bucket, filename)
    except Exception as e:
        print(f'EXCEPTION in get_file_metadata task: {str(e)}')
        raise e
    return {'result':  dictionary} 

@celery.task(bind=True)
def process_file_metadata_task(self, urn):
    print(f'Process file task {urn}')
    path = urn.split(",")[1].split("/")
    bucket, filename = path[0], "/".join(path[1:])
    print(f'Process file task {bucket} {filename}')

    self.update_state(state=states.STARTED)
    try:
        dictionary, tags = process_file(bucket, filename)
        result = update_datahub_meta(dictionary, tags, urn)
    except Exception as e:
        print(f'EXCEPTION in process_file task: {str(e)}')
        raise e
    return {'result':  result} 

    
def process_file(bucket: str, filename: str):
    dictionary = {}
    local_file_path = f'/tmp/{filename}'
    client.fget_object(bucket, filename, local_file_path)
    extension = pathlib.Path(filename).suffix
    dictionary["extension"] = extension
    tags = []

    if extension == '.zip':
        zip_obj = zipfile.ZipFile(local_file_path,"r")
        content_list = zip_obj.namelist()
        dictionary["content_list"] = str(content_list)

    dictionary = find_model_specific_meta(dictionary)    
    tags += define_tags(dictionary)
    os.remove(local_file_path)
    return dictionary, tags

def find_model_specific_meta(dictionary: dict) -> dict:
    dictionary["model_type"] = 'unknown'
    if 'content_list' in dictionary:
        if dictionary["content_list"].lower().find('modflow') != -1:
            dictionary["model_type"] = 'modflow'
        elif dictionary["content_list"].lower().find('hydrus') != -1: 
            dictionary["model_type"] = 'hydrus'

    return dictionary


def define_tags(dictionary: dict) -> list:
    tags = []
    tags.append("metadata-processed")
    tags.append(dictionary["model_type"])
    return tags

def update_datahub_meta(dictionary: dict, tags: list, urn: str) -> str:
    emitter = DatahubRestEmitter(gms_server=config.datahub_url, extra_headers={}, token=config.datahub_token)

    dataset_properties = DatasetPropertiesClass(customProperties=dictionary)
    metadata_event: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
        entityType="dataset",
        changeType=ChangeTypeClass.UPSERT,
        entityUrn=urn,
        aspectName="datasetProperties",
        aspect=dataset_properties,
    )

    # Emit metadata! This is a blocking call
    emitter.emit(metadata_event)

    print(tags)
    my_tags = [TagAssociationClass(tag=make_tag_urn(t)) for t in tags]

    tag_event: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
        entityType="dataset",
        changeType=ChangeTypeClass.UPSERT,
        entityUrn=urn,
        aspectName="globalTags",
        aspect=GlobalTagsClass(tags=my_tags),
    )

    emitter.emit(tag_event)

def list_not_processed_files(request_query: str, filtered_tag: str) -> str:
    accessToken = config.datahub_token 
    endpoint = config.graphql_endpoint
    headers = {"Authorization": f"Bearer {accessToken}"}

    query = 'query { search(input: { type: DATASET, query: "'+request_query+'", filters: [{ field: "", value: "" }] , start: 0, count: 10 })'+""" {
        start
        count
        total
        searchResults {
        entity {
            urn
            type
            ...on Dataset {
                name
                tags {
                    tags {
                        tag {
                        urn
                        }
                    }
                    }
            }
        }
        }
    }
    }"""

    r = requests.post(endpoint, json={"query": query}, headers=headers)
    if r.status_code == 200:
        files_filtered_with_tag = []
        all_files = r.json()
        if 'data' in all_files:
            for file in all_files['data']['search']['searchResults']:
                tags = file['entity']['tags']
                has_metadata_processed_tag = False
                if tags != None:
                    for tag in tags['tags']:
                        if tag['tag']['urn'] == filtered_tag:
                            has_metadata_processed_tag = True
                if has_metadata_processed_tag == False:
                    files_filtered_with_tag.append(file['entity']['urn'])
            return files_filtered_with_tag
        else:
            if 'errors' in all_files:
                return f"Query failed to run with an error:  {all_files['errors']}."
    else:
        return f"Query failed to run with a {r.status_code}."