import os

class BaseConfig():
    API_PREFIX = '/api'
    imports = ('api',)
    result_serializer = 'json'
    task_serializer = 'json'
    task_ignore_result = False
    task_track_started = True
    TESTING = False
    DEBUG = False


class DevConfig(BaseConfig):
    FLASK_ENV = 'development'
    DEBUG = True
    CELERY_broker_url = 'redis://redis:6379/0'
    result_backend = 'redis://redis:6379/0'
    minio_url = 'localhost:9000'
    minio_access_key = 'root'
    minio_secret_key = 'password'
    minio_secure = False
    host = '0.0.0.0'



class ProductionConfig(BaseConfig):
    FLASK_ENV = 'production'
    CELERY_broker_url = 'redis://redis:6379/0'
    result_backend = 'redis://redis:6379/0'
    minio_url = os.environ.get('MINIO_URL', 'minio.minio:9000')
    minio_access_key = os.environ.get('MINIO_ACCESS_KEY', 'root')
    minio_secret_key = os.environ.get('MINIO_SECRET_KEY', 'password')
    minio_secure = True
    host = os.environ.get('API_HOST', '0.0.0.0')


class TestConfig(BaseConfig):
    FLASK_ENV = 'development'
    TESTING = True
    DEBUG = True
    # make celery execute tasks synchronously in the same process
    CELERY_ALWAYS_EAGER = True