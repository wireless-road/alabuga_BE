FROM python:3.8.10

ENV APP_USER=app
ENV APP_GRP=app
ENV APP_HOME=/app
ENV APP_SHELL=/bin/bash
ENV PIPENV_VENV_IN_PROJECT=1

WORKDIR /app
EXPOSE 5000
CMD ["/app/entrypoint.sh"]
#CMD ["/app/app.py"]

RUN /bin/bash -o pipefail -c 'groupadd "${APP_GRP}" &&  useradd --create-home --home-dir "${APP_HOME}" --shell "${APP_SHELL}" --gid "${APP_GRP}" "${APP_USER}" && chown -R "${APP_USER}":"${APP_GRP}" "${APP_HOME}"'

COPY . ${APP_HOME}
RUN pwd && ls -a
RUN apt-get update -qq -y
RUN pip install pipenv uwsgi
RUN ls -la /app
RUN pipenv install
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir /var/log/uwsgi
RUN chown ${APP_USER} /var/log/uwsgi

USER ${APP_USER}
