# Identifier

A python project to provide identifiers as a service.

Identifier provides an API by which identifiers can be requested that are guaranteed to be 
unique within the context of the service instance's backing data store.

The longer-term goal of this project is to not only provide new unique identifiers, but to accept
entity data and supply existing identifiers based on identity-matching algorithms that offer the
client a customizable degree of certainty that those attributes have been matched to an entity 
already known to the instance.

## Setup

### Set environment variables

Create a file named `.env` in this project's root directory, and populate it with the following keys and your values:

    # zsh
    export COMPOSE_PROJECT_NAME=identifier_api
    export COMPOSE_FILE=docker-compose.yml
    export TLS_KEY=[String; the location of the file containing the key for the web server certificate. 
                    E.g.: ./identifier.key]
    export TLS_CERT=[String; the location of the file containing the public web server certificate. 
                     E.g.: ./identifier.crt]
    export IDENTIFIER_LOG_LEVEL=[String; Logging level for the identifier app; "DEBUG", "INFO", etc.]
    export IDENTIFIER_DATA_PATH=[String; Filepath to the directory where identifier's data will be stored]
    export IDENTIFIER_MAX_READER_COUNT=[Integer; Maximum number of read-only repository instances]
    export IDENTIFIER_MAX_RETRIES=[Integer; Maximum number of times to retry a write operation]
    export IDENTIFIER_TEXT_ENCODING=[String; Encoding scheme for text data I/O; default is "utf-8"]
    export BUILD_ID=[String; Tag for the current build of Identifier; see ./setup.cfg for the version no.]

Alternatively, set the environment variables in [docker-compose](docker-compose.yml) by specifying
their values directly, though this is not a recommended practice for security and portability
reasons.

*Suggestion*: use [mkcert](https://github.com/FiloSottile/mkcert) for creating and installing
certificates suitable for use in development (*not* in production.)

### Create a virtual environment for Python

    python3 -m venv .venv

### Activate the virtual environment and the identifier environment

    source .venv/bin/activate
    source .env

### Build the identifier package

    pip install setuptools
    pip install build
    pip install pytest
    python -m build

## Installation

This will install the identifier api in the python virtual environment:

    pip install dist/co.deability.identifier-[version]-py3-none-any.whl

## Running the Identifier API

### Manual startup

    cd src
    python -m co.deability.identifier.api.app

### Containerized startup

    sh build.sh

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

## Contributing

You can leverage tools during development to make life simpler.

### Environment

Create an additional environment file named `.env_dev` that specifies the following variables:

    export COMPOSE_FILE=docker-compose-dev.yml
    export CERT_SUBJ=[String; Subject line for a self-signed certificate for development;
                      e.g., /C=US/ST=Michigan/L=Saline/O=Codeability/CN=*.localhost]
    export LOCAL_DATA_PATH=[String; file path on a formatted block storage device mounted in the host 
                            where identifier's data will be stored when it is run inside a container;
                            see docker-compose-dev.yml]

### Build

Using the `build_dev.sh` script will shorten your build time by obviating the downloading of dependencies that are
included in the `identifier_api` image created by `build.sh`. Note that the `build.sh` script must be run at least once
prior to running `build_dev.sh`:

    sh build.sh
    ...
    sh build_dev.sh

### Pre-Commit

Identifier uses [pre-commit](https://pre-commit.com) to add hooks to git that will 
fire before a commit is accepted. Install it in your virtual environment via pip:

    pip install pre-commit

The configuration file at [.pre-commit-config.yaml](.pre-commit-config.yaml) specifies that `pytest` 
should run prior to committing local changes. Add it to your local git repository's pre-commit 
hooks script using pre-commit's installer:

    pre-commit install

### Testing

To run the available unit and integration tests manually:

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
