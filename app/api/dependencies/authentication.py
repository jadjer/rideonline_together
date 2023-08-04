#  Copyright 2022 Pavel Suprunov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from loguru import logger
from typing import Callable
from fastapi import Depends, HTTPException, Security, status

from app.api.dependencies.get_from_header import get_language
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.resources import strings_factory
from app.services.auth_token_header import AuthTokenHeader
from app.services.token import get_user_id_from_access_token


HEADER_KEY = "Authorization"


def get_current_user_authorizer() -> Callable:
    return _get_user_id_from_token


def _get_authorization_header(
        language: str = Depends(get_language),
        api_key: str = Security(AuthTokenHeader(name=HEADER_KEY)),
        settings: AppSettings = Depends(get_app_settings),
) -> str:
    strings = strings_factory.get_language(language)

    try:
        token_prefix, token = api_key.split(" ")
    except ValueError as exception:
        logger.error(exception)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, strings.WRONG_TOKEN_PREFIX)

    if token_prefix != settings.jwt_token_prefix:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, strings.WRONG_TOKEN_PREFIX)

    return token


def _get_user_id_from_token(
        language: str = Depends(get_language),
        token: str = Depends(_get_authorization_header),
        settings: AppSettings = Depends(get_app_settings),
) -> int:
    strings = strings_factory.get_language(language)

    user_id = get_user_id_from_access_token(token, settings.public_key)
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, strings.MALFORMED_PAYLOAD)

    return user_id
