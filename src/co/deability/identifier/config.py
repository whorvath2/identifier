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
import subprocess
from datetime import timezone
from pathlib import Path
from typing import Final
from co.deability.identifier.errors.EnvironmentError import EnvironmentError

debug: bool = __debug__

# BUILD INFO
commit = "N/A"
try:
    commit: str = str(
        subprocess.run(["git", "rev-parse", "@"], capture_output=True, text=True).stdout
    )
    if commit:
        commit = commit[0:8]
except FileNotFoundError:
    # No git. Meh.
    ...

BUILD_ID: Final[str] = os.environ.get("BUILD_ID", commit)


# LOGGING CONFIG
ROOT_LOG_LEVEL: Final[str] = os.environ.get("ROOT_LOG_LEVEL")
APP_LOG_LEVEL: Final[str] = os.environ.get("IDENTIFIER_LOG_LEVEL")
if not ROOT_LOG_LEVEL or not APP_LOG_LEVEL:
    raise EnvironmentError(
        explanation="Either or both of the environment variables ROOT_LOG_LEVEL and "
        "IDENTIFIER_LOG_LEVEL are not set."
    )

LOG = logging.getLogger("id_log")
try:
    logging.getLogger().setLevel(level=ROOT_LOG_LEVEL)
    LOG.setLevel(level=APP_LOG_LEVEL)
except ValueError:
    raise EnvironmentError(
        explanation="Either or both of the environment variables ROOT_LOG_LEVEL and "
        "IDENTIFIER_LOG_LEVEL are set to an unsupported value; use only CRITICAL, FATAL, "
        "ERROR, WARN, WARNING, INFO, or DEBUG."
    )


# DATA CONFIG
_data_path: str = os.environ.get("IDENTIFIER_DATA_PATH")
if not _data_path:
    raise EnvironmentError(
        explanation="The IDENTIFIER_DATA_PATH environment variable is not set."
    )
DATA_PATH: Final[Path] = Path(_data_path).absolute()
LOG.info(f"Constructing data path {DATA_PATH}")
DATA_PATH.mkdir(parents=True, exist_ok=True)
SCHEMA_PATH: Final[Path] = Path(DATA_PATH, "schema")
SCHEMA_PATH.mkdir(parents=False, exist_ok=True)
MAX_READER_COUNT: int = int(os.environ.get("IDENTIFIER_MAX_READER_COUNT", 1))
MAX_WRITE_RETRIES: int = int(os.environ.get("IDENTIFIER_MAX_RETRIES", 0))
IDENTIFIER_LENGTH: int = int(os.environ.get("IDENTIFIER_ID_LENGTH", 32))
if IDENTIFIER_LENGTH > 128 or IDENTIFIER_LENGTH <= 16:
    raise EnvironmentError(
        "The IDENTIFIER_ID_LENGTH must be between 16 and 128 (inclusive.)"
    )

# OTHER CONFIG
TIMEZONE: timezone = timezone.utc
TEXT_ENCODING: str = str(os.environ.get("IDENTIFIER_TEXT_ENCODING", "utf-8"))
# Verify text encoding value
try:
    " ".encode(TEXT_ENCODING)
except LookupError:
    raise EnvironmentError(
        explanation="The IDENTIFIER_TEXT_ENCODING variable is missing or has an unsupported value."
    )

# Report out
LOG.info("Config loaded")
LOG.debug(
    str(
        {
            "ROOT_LOG_LEVEL": ROOT_LOG_LEVEL,
            "APP_LOG_LEVEL": APP_LOG_LEVEL,
            "DATA_PATH": DATA_PATH,
            "MAX_READER_COUNT": MAX_READER_COUNT,
            "MAX_WRITE_RETRIES": MAX_WRITE_RETRIES,
            "TEXT_ENCODING": TEXT_ENCODING,
            "TIMEZONE": TIMEZONE,
            "BUILD_ID": BUILD_ID,
        }
    )
)
