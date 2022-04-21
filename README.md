# Metadata Service

Service written in Python Flask, using Celery to handle tasks of metadata detection.
# Startup using docker 
``` bash
$ APP_ENV=Dev docker compose up --build
```


# Publishing new version
To publish new version (eg. `1.0.0`) on docker registry just do 
``` bash
$ git tag v1.0.0 
$ git push origin v1.0.0
```