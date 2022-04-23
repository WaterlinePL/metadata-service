import time

from minio import Minio

import logging

logger = logging.getLogger()

client = Minio("127.0.0.1:9000",
    access_key='minioadmin',
    secret_key='minioadmin', secure=False)

# self.update_state(state=celery.states.FAILURE, meta="Reason")
if client.bucket_exists('input'):
    logger.log("input bucket exists",level=logging.DEBUG)
else:
    client.make_bucket('input')

