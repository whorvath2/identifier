FROM python:3-slim-buster

ARG environment_type
ARG build_id

ENV FLASK_ENV=$environment_type
ENV BUILD_ID=$build_id

RUN apt-get update \
    && apt-get install -y nginx openssl supervisor \
    && mkdir /srv/flask_app \
    && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout /etc/ssl/private/codeability-selfsigned.key \
    -out /etc/ssl/certs/codeability-selfsigned.crt \
    -subj "/C=US/ST=Michigan/L=Saline/O=Codeability/CN=*.deability.co"

WORKDIR /srv/flask_app
COPY . /srv/flask_app
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisord.conf
COPY requirements.txt /srv/flask_app/requirements.txt

ENV VIRTUAL_ENV=.venv

RUN python -m venv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/pip install -r requirements.txt

ENV PATH=$PATH:$VIRTUAL_ENV/bin

RUN chown -R www-data:www-data /var/lib/nginx

EXPOSE 443
ENTRYPOINT ["/usr/bin/supervisord"]
