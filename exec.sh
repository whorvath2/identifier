#!/bin/zsh

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

podman container stop identifier_api
podman container rm -f identifier_api
podman run -d -t \
--name=identifier_api \
--secret identifier_cert_key,type=mount,target=/etc/ssl/private/identifier.key,mode=0440 \
--secret identifier_cert_pub,type=mount,target=/etc/ssl/certs/identifier.crt,mode=0444 \
--secret identifier_cert_ca_pub,type=mount,target=/usr/local/share/ca-certificates/identifier_ca.crt,mode=0444 \
localhost/identifier_api_image:latest
