# Identifier

An API to provide entity identifiers and user-defined search indexing as a service.

Identifier provides an API by which identifiers for entities can be requested that are guaranteed to be unique within the context of the service instance's backing data store. The API also allows the client to specify any arbitrary JSON document as search terms for any particular entity. For a detailed example, see *Principles of Operation: Use Case Example*, below

## Principles of Operation

### Data Storage

Identifier is designed to use a block file system as the data store for the identifiers it generates, with the user-configurable IDENTIFIER_DATA_PATH being the parent directory. Each identifier value is stored as a folder hierarchy when it is generated, such that each character of the identifier is a directory. _E.g._, an identifier value of `foobar` is serialized into the file system at `<IDENTIFIER_DATA_PATH>/f/o/o/b/a/r/`.

The length of the identifiers used in any particular Identifier instance are user-configurable via the environment variable `IDENTIFIER_ID_LENGTH`, which (if specified) must be a value between 16 and 128 inclusive. The default value is 32.

For performance reasons, it is recommended that identifier containers use the file system on the host VM for the backing data store, and that the host VM use direct-attached drives (as opposed to NFS or SMB mounts) for storage.

#### Workflows

The Identifier API is designed to support the following general workflows:

*Entity Creation, Updating, and Deletion*

* POST + entity data -> Receive entity identifier + success code
* UPDATE + entity identifier + entity data -> Receive new entity identifier + success code
* DELETE + entity identifier -> Receive success code

*Search Term Creation and Deletion*

* POST + entity identifier + search term document -> Receive success code
* DELETE + search term -> Receive success code

*Entity Search*

* GET request + identifier -> Receive entity data + success code
* GET entity search request + search term document -> Receive list of entity identifiers and entity data + success code
* GET entity identifier search request + search term document -> Receive list of entity identifiers + success code

In the current release, both entity data and search term data must be JSON documents. This will likely change in a future version of the API.

Identifier stores entities and create identifiers for them that reflect the content of the entity's data; i.e., identifier generation for entities is _deterministic_, rather than random or incremental. If an attempt is made to re-add an entity that is already known to the Identifier instance, an error will be returned.

When an entity is updated, a new identifier for the entity is generated, and the previous data file is replaced with a link to the new entity data file. Subsequent read requests using either the old or new identifier values will both return the same (current) entity data in the response.

Any particular search term can be attached to more than one entity identifier, so that a list of matching entity identifiers (and, optionally, entity data) can be retrieved by that term.

#### Workflow Use Case Example

A healthcare provider wants to use Identifier to store patients, and to be able to find patients by a combination of first name, last name, and birthday. They configure their client to add a patient entity to Identifier, and after receiving that patient's identifier in response, they add a search index for that identifier consisting of that patient's first name, last name, and birthday. They can then submit the same index to retrieve any matching pateint entities:

    REQUEST                                                                 RESPONSE

    POST https://<identifier host>/add/Patient                              202 
    {                                                                       {
        "MRN": "0123456789",                                                    "created": "<unique identifier>"
        "First Name": "William"                                             }
        ...
    }                                                                      

    POST https://<identifier host>/index/add/<unique identifier>            200
    {
        "First": "William", 
        "Last": "Horvath", 
        "Birthday": "01/01/1970"
    }

    GET https://<identifier host>/search                                    200
    {                                                                       [{
        "First": "William",                                                     "<unique identifier>": {  
        "Last": "Horvath",                                                          {
        "Birthday": "01/01/1970"                                                        "MRN": "0123456789",
    }                                                                                   "First Name": "William",
                                                                                        ...
                                                                                    },
                                                                                 },
                                                                                "<unique identifier 2>": {
                                                                                    {
                                                                                        "MRN": "222222222",
                                                                                        "First Name": "Aimee",
                                                                                        ...
                                                                                    }
                                                                            }]

##### Search Indexing

Identifier can accept any JSON document as a search term for one or more existing entity identifiers. When the user adds a search term and an identifier for an entity to which that term refers, an identifier file for the search term is created which links directly back to the entity file. 

The same search term can be linked to any arbitrary number of already-storied entity identifiers, and those entities or their identifiers can be retrieved by using the search term in the body of subsequent GET requests to the appropriate `search` endpoints.

##### Entity Validation

Identifier supports validation of entities being POSTed for storage by way of user-supplied JSON schema for each entity type. Schema can be created, read, updated, and deleted via corresponding API endpoints that accept the schema and a name for the entity type to which it applies. Once added to an Identifier instance, they will automatically be applied to validate entities of the corresponding type when those entities are added to that instance. When validation fails, the client will receive an error code and informative message indicating that the entity failed validation.

## Setup

### Set environment variables

The environment variables used by Identifier include the following:

    # Required
    ROOT_LOG_LEVEL = [String; logging level for the runtime environmment; "DEBUG", "INFO", etc.]
    IDENTIFIER_DATA_PATH = [String; Filepath to the directory where Identifier's data will be stored.]
    IDENTIFIER_LOG_LEVEL = [String; Logging level for the Identifier app; "DEBUG", "INFO", etc.]

    # Optional
    IDENTIFIER_MAX_READER_COUNT = [Integer; Maximum number of read-only repository instances; default is 1]
    IDENTIFIER_MAX_RETRIES = [Integer; Maximum number of times to retry a write operation; default is 0]
    IDENTIFIER_TEXT_ENCODING = [String; Encoding scheme for text data I/O; default is utf-8]
    FLASK_ENV = [String; sets Flask's operating mode; legal values are "development" or "production"; default is "production"]

_Note: The `build.sh` shell script included in this repository expects to source these environment variables from a file called `.env` in the same directory as the script. If you are operating in a development environment, you can also override the default values by re-specifying them in a file named `.dev_env`, which the build script will also source after `.env`. For example:_ 
    
    # ./.env:
    export IDENTIFIER_DATA_PATH="/var/identifier/data"
    export IDENTIFIER_LOG_LEVEL="INFO"
    export IDENTIFIER_MAX_READER_COUNT=3
    export IDENTIFIER_MAX_RETRIES=3
    export IDENTIFIER_TEXT_ENCODING="utf-8"
    export ROOT_LOG_LEVEL="INFO"
    export FLASK_ENV="production"

    # ./.dev-env:
    export IDENTIFIER_DATA_PATH="$HOME/sandbox/data"
    export IDENTIFIER_LOG_LEVEL="debug"
    export ROOT_LOG_LEVEL="debug"
    export FLASK_ENV="development"

### Build Method 1: build.sh

The `build.sh` script can be used to create a podman/docker image suitable for running the Identifier application in a container:

    sh build.sh

### Build Method 2: Manual Build

As with any Flask-based Python application, Identifier can be built from the command line as well.

#### Create and activate a virtual environment for Python

    python3 -m venv .venv
    source .venv/bin/activate

#### Build and install the identifier package

    pip install setuptools
    pip install build
    python -m build

The build process will create the `dist` subdirectory, and put a Python package file for Identifier in it. You can use it to install the Identifier api in the python virtual environment as follows:

    pip install dist/co.deability.identifier-[version]-py3-none-any.whl

## Running the Identifier API

### Containerized startup

    sh exec.sh

### Manual startup

    python -m co.deability.identifier.api.app

[Open your browser](https://localhost:4336/identifier) to verify that it's running, or use `curl`:

    curl https://localhost:4336/identifier

The output should look like this:

    {
        "build_id": "local"
        "status": "OK",
        "timestamp": "Fri, 11 Feb 2022 17:10:13 +0000"
        ...
    }

_Note: additional information is included in pre-production environments_

## Contributing

You can leverage tools during development to make life simpler.

### Pre-Commit

Identifier uses [pre-commit](https://pre-commit.com) to add hooks to git that will 
fire before a commit is accepted. Install it in your virtual environment via pip:

    pip install pre-commit

The configuration file at [.pre-commit-config.yaml](.pre-commit-config.yaml) specifies that `pytest` 
should run prior to committing local changes. Add it to your local git repository's pre-commit 
hooks script using pre-commit's installer:

    pre-commit install

### Testing

To run the available unit and integration tests manually, run pytest:

    pytest

___
_Copyright © 2021 William L Horvath II_

_Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License
at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0) Unless
required by applicable law or agreed to in writing, software distributed under the License is
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing permissions and limitations under the
License._
