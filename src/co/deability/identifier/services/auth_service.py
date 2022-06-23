from pathlib import Path
from typing import Callable, Final, Dict, Any
import functools
import jwt
from flask import request

from co.deability.identifier.errors.BadJwtError import BadJwtError

KEY_ALGORITHM: Final[str] = "EdDSA"
USER_ID_KEY: Final[str] = "user_id"


def authenticate(func: Callable):
    @functools.wraps(func)
    def authenticator(*args, **kwargs):
        token: str = _get_jwt()
        return func(*args, **kwargs)

    return authenticator


def _get_jwt() -> [str, None]:
    bearer_token: str = request.headers.get("Authorization")
    bearer: str = "Bearer "
    if not bearer_token or not bearer_token.startswith(bearer):
        raise BadJwtError()
    return bearer_token[len(bearer) :]


def _get_user(token: str):
    pub_path: Path = Path(Path.home(), ".ssh", "id_identifier.pub")
    public_key: str = open(pub_path).read()
    payload: Dict[str, Any] = jwt.decode(token, public_key, algorithms=[KEY_ALGORITHM])
    return payload.get(USER_ID_KEY)


def _create_jwt(user_id: str):
    private_path: Path = Path(Path.home(), ".ssh", "id_identifier")
    private_key: str = open(private_path).read()
    token: str = jwt.encode(
        {USER_ID_KEY: user_id}, private_key, algorithm=KEY_ALGORITHM
    )
    return token
