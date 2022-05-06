# Identifier

A python project to provide identifiers as a service.

Identifier provides an API by which identifiers can be requested that are guaranteed to be 
unique within the context of the service instance's backing data store.

The longer-term goal of this project is to not only provide new unique identifiers, but to accept
entity data and supply existing identifiers based on identity-matching algorithms that offer the
client a customizable degree of certainty that those attributes have been matched to an entity 
already known to the instance.

## Setup

### Create a virtual environment for Python

    python3 -m venv .venv

### Set environment variables

Create a .env file in the root directory, and populate it with the following keys and your values:

    IDENTIFIER_DATA_PATH=[String; Filepath to the directory on the host in which identifier's data will be stored]
    IDENTIFIER_LOG_LEVEL=[String; Logging level for the identifier app; "DEBUG", "INFO", etc.]
    BUILD_ID=[String; Tag for the current build of Identifier; see ./setup.cfg for the version no.]
    FLASK_ENV=[String; Flask's environment setting - development, production, etc.]
    IUID=[Integer; value for the user ID for the owner of the identifier process; e.g. 1001]
    IGID=[Integer; value for the group ID for the owner of the identifier process; e.g. 1002]
    IDENTIFIER_MAX_READER_COUNT=[Integer; Maximum number of reader repository instances]
    IDENTIFIER_MAX_RETRIES=[Integer; Maximum number of times to retry a write operation]
    CERT_SUBJ=[String; Subject line for the self-signed certificate; e.g., "/C=US/ST=Michigan/L=Saline/O=Codeability/CN=*.localhost"]

Alternatively, set the environment variables in [docker-compose](docker-compose.yml) by specifying
their values directly, though this is not a recommended practice for security and transportability
reasons.

*Suggestion*: use [mkcert](https://github.com/FiloSottile/mkcert) for creating and installing
certificates suitable for use in development (*not* in production.)

### Activate the virtual environment and the identifier environment

    source .venv/bin/activate
    source .env

### Build identifier

    pip install setuptools
    pip install build
    pip install pytest
    python -m build

## Installation

### Install the distribution file

This will install the identifier api in the python virtual environment:

    pip install dist/co.deability.identifier-[version]-py3-none-any.whl

## Running the Identifier API

### Manual startup

    cd src
    ROOT_LOG_LEVEL=INFO APP_LOG_LEVEL=DEBUG python -m co.deability.identifier.api.app

### Containerized startup

    docker-compose -p identifier up

[Open your browser](https://localhost:4430/identifier) to verify that it's running, or use `curl`:

    curl https://localhost:4430/identifier

The output should look like this:

    {
        "build_id": "local"
        "status": "OK",
        "timestamp": "Fri, 11 Feb 2022 17:10:13 +0000"
        ...
    }

Note: additional information is included in pre-production environments

## Development

### Testing

    pytest src/tests

___
_Copyright © 2021 William L Horvath II_

_Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License
at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0) Unless
required by applicable law or agreed to in writing, software distributed under the License is
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing permissions and limitations under the
License._
