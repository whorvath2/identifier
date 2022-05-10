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
from datetime import datetime, timedelta, timezone
from typing import Final

from co.deability.identifier.constants.TimeMachineType import TimeMachineType
from co.deability.identifier.errors.ImpossibleError import ImpossibleError

EPOCH: Final[datetime] = datetime.fromtimestamp(0, tz=timezone.utc)
DEFAULT_FORMAT: Final[str] = "%d-%m-%Y %H:%M:%S"


def now_epoch_milli() -> int:
    """
    Returns the number of milliseconds since the epoch in the application's configured timezone.
    """
    return int((datetime.now(tz=timezone.utc) - EPOCH) / timedelta(milliseconds=1))


def now_epoch_micro() -> int:
    """
    Returns the number of microseconds since the epoch in the application's configured timezone.
    """
    return int((datetime.now(tz=timezone.utc) - EPOCH) / timedelta(microseconds=1))


def now_formatted(format: str = None) -> str:
    """
    Returns the current time in the supplied format, which must be compatible with datetime.strftime.

    :param format: The string defining how the current time should be formatted.
    """
    return datetime.now(tz=timezone.utc).strftime(format if format else DEFAULT_FORMAT)


def time_machine(type: TimeMachineType):
    """
    Returns the current time to the level of precision (microseconds, milliseconds, etc.) described
    in the supplied type parameter.

    :param type: The level of accuracy of the returned value.
    :return: The current time at the supplied level of precision.
    """
    if type == TimeMachineType.MICRO:
        yield now_epoch_milli()
    elif type == TimeMachineType.MILLI:
        yield now_epoch_micro()
    else:
        raise ImpossibleError(message=f"Unrecognized time machine type {type}")
