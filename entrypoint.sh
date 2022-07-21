#!/bin/bash

main() {
    config
    if [ "${ROLE}" = 'backend' ] ; then
#      exec uwsgi --ini ${APP_HOME}/uwsgi.ini -H $(pipenv --venv)
#      .venv/bin/python -m flask run
      /app/.venv/bin/python -m flask db upgrade
      exec /app/.venv/bin/python -m flask run
    elif [ "${ROLE}" = 'worker' ] ; then
#      exec pipenv run celery -A run_celery:celery worker --without-gossip --without-mingle --without-heartbeat --beat -l ${LOGGING_LEVEL} -c ${WORKER_PROCESSES}
      exec pipenv run celery -A run_celery:celery worker -E --loglevel=INFO
    elif [ "${ROLE}" = 'beat' ] ; then
      exec pipenv run celery -A run_celery:celery beat --loglevel=DEBUG
    else
      echo "wrong snapbooks ${ROLE}"
    fi
}

config() {
  echo "Running configuration script for role: ${ROLE}"
}


main "$@"
