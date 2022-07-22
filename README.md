# Metadata Service

Service written in Python Flask, using Celery to handle tasks of metadata detection.
# Startup using docker - for local development
``` bash
$ docker network create -d bridge waterline

$ APP_ENV=Dev docker compose up --build
```

# Kubernetes setup
``` bash
$ kubectl apply -f k8s/metadata-ns.yaml

$ kubectl create secret generic env-secrets   --from-literal=API_HOST='<api_host>'   --from-literal=MINIO_URL='<minio_url>'   --from-literal=MINIO_ACCESS_KEY='<minio_access_key>'   --from-literal=MINIO_SECRET_KEY='<minio_secret_key' --from-literal=DATAHUB_GMS_URL='http://datahub-datahub-gms.data.svc.cluster.local:8080' --from-literal=DATAHUB_GRAPHQL_URL='http://datahub-datahub-frontend.data.svc.cluster.local:8080' --from-literal=DATAHUB_TOKEN='<personal_token>' -n metadata

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