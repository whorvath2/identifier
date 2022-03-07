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
    return int((datetime.now(tz=timezone.utc) - EPOCH) / timedelta(microseconds=1))


def now_formatted(format: str = None) -> str:
    return datetime.now(tz=timezone.utc).strftime(format if format else DEFAULT_FORMAT)


def time_machine(type: TimeMachineType):
    if type == TimeMachineType.MICRO:
        yield now_epoch_milli()
    elif type == TimeMachineType.MILLI:
        yield now_epoch_micro()
    else:
        raise ImpossibleError(message=f"Unrecognized time machine type {type}")
