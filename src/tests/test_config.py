import os
from importlib import reload
from typing import Final

import pytest
from co.deability.identifier import config

RLL: Final[str] = "ROOT_LOG_LEVEL"
ILL: Final[str] = "IDENTIFIER_LOG_LEVEL"
IDP: Final[str] = "IDENTIFIER_DATA_PATH"
ITE: Final[str] = "IDENTIFIER_TEXT_ENCODING"


def _set_log_levels(root: str, app: str):
    os.environ[RLL] = root
    os.environ[ILL] = app


def test_missing_or_unsupported_log_levels():
    REX: Final[str] = f"(.*?{ILL}|{RLL})" + "{2}"
    with pytest.raises(SystemExit) as wrapped_error:
        _set_log_levels(root="", app="DEBUG")
        reload(config)
        wrapped_error.match(REX)
    with pytest.raises(SystemExit) as wrapped_error:
        _set_log_levels(root="INFO", app="")
        reload(config)
        wrapped_error.match(REX)
    with pytest.raises(SystemExit) as wrapped_error:
        _set_log_levels(root="INFO", app="foobar")
        reload(config)
        wrapped_error.match(REX)
    with pytest.raises(SystemExit) as wrapped_error:
        _set_log_levels(root="foobar", app="INFO")
        reload(config)
        wrapped_error.match(REX)


def test_missing_data_path():
    with pytest.raises(SystemExit) as wrapped_error:
        os.environ[IDP] = ""
        reload(config)
        wrapped_error.match(f".*({IDP})")


def test_bad_or_missing_encoding():
    with pytest.raises(SystemExit) as wrapped_error:
        os.environ[ITE] = ""
        reload(config)
        wrapped_error.match(f".*{ITE}")
    with pytest.raises(SystemExit) as wrapped_error:
        os.environ[ITE] = "foobar_encoding"
        reload(config)
        wrapped_error.match(f".*{ITE}")


def test_good_encoding():
    os.environ[ITE] = "ascii"
    reload(config)
    assert config.TEXT_ENCODING == "ascii"
