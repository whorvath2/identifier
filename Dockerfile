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

FROM python:3.9

ARG guid
ARG uuid
ARG identifier_log_level
ARG identifier_data_path
ARG identifier_max_reader_count
ARG identifier_max_retries
ARG flask_env
ARG build_id
ARG cert_subj

ENV APP_LOG_LEVEL=$identifier_log_level
ENV BUILD_ID=$build_id
ENV CERT_SUBJ=$cert_subj
ENV FLASK_ENV=$flask_env
ENV IDENTIFIER_DATA_PATH=$identifier_data_path
ENV IDENTIFIER_MAX_READER_COUNT=$identifier_max_reader_count
ENV IDENTIFIER_MAX_RETRIES=$identifier_max_retries
ENV IDENTIFIER_TEXT_ENCODING=$identifier_text_encoding
ENV ROOT_LOG_LEVEL=INFO
ENV VIRTUAL_ENV=.venv

RUN apt-get update
RUN apt-get install -y nginx supervisor openssl

RUN groupadd -g $guid api-service \
    && useradd -d /service/identifier -s /bin/bash -u $uuid -g $guid api-service \
    && mkdir -p /service/identifier \
    && mkdir -p $identifier_data_path \
    && chown -R api-service:api-service /service/identifier \
    && chown -R api-service:api-service $identifier_data_path \
    && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout /etc/ssl/private/identifier-selfsigned.key \
    -out /etc/ssl/certs/identifier-selfsigned.crt \
    -subj $cert_subj

WORKDIR /service/identifier
COPY . /service/identifier
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisord.conf

RUN python -m venv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/python -m pip install --upgrade pip \
    && $VIRTUAL_ENV/bin/pip install setuptools \
    && $VIRTUAL_ENV/bin/pip install build \
    && $VIRTUAL_ENV/bin/python -m build --wheel -o ./ \
    && $VIRTUAL_ENV/bin/pip install ./*.whl

ENV PATH=$PATH:$VIRTUAL_ENV/bin

EXPOSE 443
ENTRYPOINT ["/usr/bin/supervisord", "-c", "/service/identifier/supervisord.conf"]
