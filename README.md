# Metadata Service

Service written in Python Flask, using Celery to handle tasks of metadata detection.
# Startup using docker - for local development
``` bash
docker network create -d bridge waterline

$ APP_ENV=Dev docker compose up --build
```

# Kubernetes setup
```
$ kubectl apply -f k8s/metadata-ns.yaml

# Dev setup:
$ kubectl create configmap svc-config --from-env-file=dev.properties -n metadata

# Prod setup:
$ kubectl create configmap svc-config --from-env-file=prod.properties -n metadata

$ kubectl apply -f k8s/
```
# Publishing new version
To publish new version (eg. `1.0.0`) on docker registry just do 
``` bash
$ git tag v1.0.0 
$ git push origin v1.0.0
```