import json
from typing import Dict, Any
from flask import request
import jsonschema
from jsonschema.exceptions import ValidationError

from co.deability.identifier import config
from co.deability.identifier.errors.BadRequestError import BadRequestError
from co.deability.identifier.errors.UnknownEntityTypeError import UnknownEntityTypeError


def validate_entity(post_func):
    def validator(*args, **kwargs):
        entity: Dict[str, Any] = request.json
        if not entity:
            raise BadRequestError(
                message="The body cannot be missing or an empty document."
            )
        entity_type: str = request.url.rsplit(sep="/", maxsplit=1)[1]
        schema = known_schema().get(entity_type)
        if not schema:
            raise UnknownEntityTypeError()
        try:
            jsonschema.validate(instance=entity, schema=schema)
        except ValidationError as ve:
            raise BadRequestError(
                message="The entity cannot be validated against the specified entity type."
            )
        return post_func(*args, **kwargs)

    return validator


def known_schema() -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for schema in config.SCHEMA_PATH.glob("**/*.json"):
        result.update(
            {schema.stem: json.loads(schema.read_text(encoding=config.TEXT_ENCODING))}
        )
    return result
