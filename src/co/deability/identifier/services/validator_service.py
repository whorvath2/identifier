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
        if config.DEBUG:
            return post_func(*args, **kwargs)
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
