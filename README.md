# Alabuga CORE service

Alabuga backend developed as test task

## Getting started:

Run:
```
$ docker-compose up -d
```

As a result you should see 5 docker containers. Something like that:
```
$ docker ps
CONTAINER ID   IMAGE                                COMMAND                  CREATED AT                      STATUS                       NAMES
e0f7d8758693   alabuga_backend                      "/app/entrypoint.sh"     2022-04-03 11:48:33 +0300 MSK   Up 11 minutes                alabuga_alabuga_worker_1
cb0def7c75fa   alabuga_backend                      "/app/entrypoint.sh"     2022-04-03 11:48:33 +0300 MSK   Up 11 minutes                alabuga_alabuga_backend_1
a3fa7088e5cf   alabuga_backend                      "/app/entrypoint.sh"     2022-04-03 11:48:33 +0300 MSK   Up 11 minutes                alabuga_alabuga_beat_1
5a4ca71add1b   redis:6.0.8-alpine                   "docker-entrypoint.s…"   2022-04-03 11:48:32 +0300 MSK   Up 11 minutes (healthy)      alabuga_alabuga_redis_1
0949dac10e9e   postgres:11.9                        "docker-entrypoint.s…"   2022-04-03 11:48:32 +0300 MSK   Up 11 minutes (healthy)      alabuga_alabuga_postgres_1
```

here:
```
alabuga_backend_1 - is backend service that handles all API requests from FE
alabuga_postgres_1 - is test postgres database. ATTENTION! Don't use containerized DB in production!
alabuga_redis_1 - redis DB used as message broker for celery
alabuga_beat_1 - celery beat service
alabuga_worker_1 - celery worker service
```


