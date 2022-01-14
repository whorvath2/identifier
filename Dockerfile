# Copyright © 2021 William L Horvath II
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3-slim-buster

ARG environment_type
ARG build_id

ENV FLASK_ENV=$environment_type
ENV BUILD_ID=$build_id

RUN apt-get update \
    && apt-get install -y nginx openssl supervisor \
    && mkdir /service/identifier \
    && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout /etc/ssl/private/codeability-selfsigned.key \
    -out /etc/ssl/certs/codeability-selfsigned.crt \
    -subj "/C=US/ST=Michigan/L=Saline/O=Codeability/CN=*.deability.co"

WORKDIR /service/identifier
COPY . /service/identifier
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisord.conf

ENV VIRTUAL_ENV=.venv

RUN python -m venv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/pip install setuptools \
    && $VIRTUAL_ENV/bin/pip install build \
    && $VIRTUAL_ENV/bin/python -m build

ENV PATH=$PATH:$VIRTUAL_ENV/bin

RUN chown -R api-service:api-service /var/lib/nginx

EXPOSE 443
ENTRYPOINT ["/usr/bin/supervisord"]
