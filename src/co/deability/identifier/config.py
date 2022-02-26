"""
Copyright © 2021 William L Horvath II

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import logging
from pathlib import Path
from typing import Final
from co.deability.identifier.errors.EnvironmentError import EnvironmentError

# INFO
BUILD_ID: Final[str] = os.environ.get("BUILD_ID", "N/A")

# LOGGING CONFIG
ID_LOG: Final[str] = "id_log"
ROOT_LOG_LEVEL: Final[str] = os.environ.get("ROOT_LOG_LEVEL")
APP_LOG_LEVEL: Final[str] = os.environ.get("APP_LOG_LEVEL")
if not ROOT_LOG_LEVEL or not APP_LOG_LEVEL:
    raise EnvironmentError(
        explanation="Either or both of the environment variables ROOT_LOG_LEVEL and "
        "APP_LOG_LEVEL are not set."
    )
logging.basicConfig(level=ROOT_LOG_LEVEL)
LOG = logging.getLogger(ID_LOG)
LOG.setLevel(level=APP_LOG_LEVEL)

# DATA CONFIG
_data_path: str = os.environ.get("IDENTIFIER_DATA_PATH")
if not _data_path:
    raise EnvironmentError(
        explanation="The IDENTIFIER_DATA_PATH environment variable is not set."
    )
IDENTIFIER_DATA_PATH: Final[Path] = Path(_data_path).absolute()
LOG.info(f"Constructing data path {IDENTIFIER_DATA_PATH}")
IDENTIFIER_DATA_PATH.mkdir(parents=True, exist_ok=True)

MAX_READER_COUNT: int = int(os.environ.get("IDENTIFIER_MAX_READER_COUNT", 1))
# Configurable because we may be using NFS
MAX_RETRIES: int = int(os.environ.get("IDENTIFIER_MAX_RETRIES", 0))
LOG.info("Config loaded")
LOG.debug(
    str(
        {
            "ROOT_LOG_LEVEL": ROOT_LOG_LEVEL,
            "APP_LOG_LEVEL": APP_LOG_LEVEL,
            "IDENTIFIER_DATA_PATH": IDENTIFIER_DATA_PATH,
            "MAX_READER_COUNT": MAX_READER_COUNT,
            "MAX_RETRIES": MAX_RETRIES,
        }
    )
)
