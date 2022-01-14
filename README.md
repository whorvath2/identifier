# identifier
A python project to provide identifiers as a service.

## Setup

From the command line:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install setuptools
    pip install build
    pip install pytest
    pip install -e .
    python -m build


## Running the API

From the command line:

    cd src
    python -m co.deability.identifier.api.app

[Open your browser](http://localhost:5000/identifier) to verify that it's running. 

___
_Copyright © 2021 William L Horvath II_

_Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0) Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License._
