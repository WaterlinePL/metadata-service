from asyncio.log import logger
from minio import Minio

import logging
import config

def init_buckets(buckets):
    logger = logging.getLogger()
    client = Minio(config.minio_url,
    access_key=config.minio_access_key,
    secret_key=config.minio_secret_key, 
    secure=config.minio_secure)

    for bucket in buckets:
        if client.bucket_exists(bucket):
            logger.log(msg=f'{bucket} bucket exists',level=10)
        else:
            client.make_bucket(bucket)