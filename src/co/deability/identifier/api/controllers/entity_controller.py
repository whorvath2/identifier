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
from http import HTTPStatus

from flask import Blueprint, jsonify, make_response, request, Response

from co.deability.identifier.api.services import entity_service
from co.deability.identifier.services.validator_service import validate_entity

entity_blueprint: Blueprint = Blueprint(
    "entity", __name__, url_prefix="/identifier/entity"
)


@entity_blueprint.get("/read/{identifier}")
def get_entity(identifier: str):
    return make_response(
        entity_service.get_entity(identifier=identifier), HTTPStatus.OK
    )


@validate_entity
@entity_blueprint.post("/add/{entity_type}")
def add_entity(entity_type: str) -> Response:
    return make_response(
        jsonify(entity_service.add_entity(entity=request.json)),
        HTTPStatus.CREATED,
    )


@entity_blueprint.post("/archive/{identifier}")
def remove_entity(identifier: str) -> Response:
    entity_service.remove_entity(identifier=identifier)
    return make_response(HTTPStatus.NO_CONTENT)


@validate_entity
@entity_blueprint.post("/update/{identifier}")
def update_entity(identifier: str) -> Response:
    return make_response(
        jsonify(
            entity_service.update_entity(identifier=identifier, entity=request.json)
        ),
        HTTPStatus.OK,
    )


@validate_entity
@entity_blueprint.post("/index/add/{identifier}")
def add_index(identifier: str) -> Response:
    entity_service.add_search_terms(identifier=identifier, search_terms=request.json)
    return make_response(HTTPStatus.NO_CONTENT)


@entity_blueprint.delete("/index/remove/{index_identifier}")
def remove_index(index_identifier: str) -> Response:
    entity_service.remove_search_index(index_identifier=index_identifier)
    return make_response(HTTPStatus.NO_CONTENT)


@entity_blueprint.get("/search/entities")
def find_entities() -> Response:
    return jsonify(
        entity_service.search_for_entities(index_terms=request.json), HTTPStatus.OK
    )


@entity_blueprint.get("/search/entities/ids")
def find_entity_identifiers() -> Response:
    return jsonify(
        entity_service.search_for_entity_ids(index_terms=request.json), HTTPStatus.OK
    )
