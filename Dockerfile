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
ARG identifier_data_path

RUN apt-get update
RUN apt-get install -y nginx supervisor openssl

RUN --mount=type=secret,id=identifier_cert_key \
    ln -s /run/secrets/identifier_cert_key /etc/ssl/private/identifier-key.pem
RUN --mount=type=secret,id=identifier_cert_pub \
    cat /run/secrets/identifier_cert_pub > /etc/ssl/certs/identifier.pem
RUN --mount=type=secret,id=identifier_cert_ca_pub \
    cat /run/secrets/identifier_cert_ca_pub > /usr/local/share/ca-certificates/identifier_ca.crt \
    && chmod 644 /usr/local/share/ca-certificates/identifier_ca.crt \
    && /usr/sbin/update-ca-certificates \
    && ln -s /usr/local/share/ca-certificates/identifier_ca.crt /usr/lib/ssl/certs/identifier_ca.crt \
    && ln -s /etc/ssl/private/identifier-key.pem /usr/lib/ssl/cert.pem

RUN groupadd -g $guid api-service \
    && useradd --no-log-init -d /service/identifier -s /bin/bash -u $uuid -g $guid api-service \
    && mkdir -p /service/identifier \
    && mkdir -p /service/identifier/.ssh \
    && mkdir -p $identifier_data_path \
    && chown -R api-service:api-service /service/identifier \
    && chown -R api-service:api-service $identifier_data_path

WORKDIR /service/identifier
COPY . /service/identifier
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisord.conf

ENV VIRTUAL_ENV=.venv
RUN python -m venv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/python -m pip install --upgrade pip \
    && $VIRTUAL_ENV/bin/pip install setuptools \
    && $VIRTUAL_ENV/bin/pip install build \
    && $VIRTUAL_ENV/bin/python -m build --wheel -o ./ \
    && $VIRTUAL_ENV/bin/pip install ./*.whl \
    && $VIRTUAL_ENV/bin/pip config set global.cert /etc/ssl/certs/ca-certificates.crt

ENV PATH=$PATH:$VIRTUAL_ENV/bin

EXPOSE 443
ENTRYPOINT ["/usr/bin/supervisord", "-c", "/service/identifier/supervisord.conf"]
