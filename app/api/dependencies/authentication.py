#  Copyright 2022 Pavel Suprunov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from httpx import AsyncClient, ConnectError
from loguru import logger
from fastapi import Depends, HTTPException, status, Security

from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.models.domain.user import User
from app.models.schemas.user import UserResponse
from app.models.schemas.wrapper import WrapperResponse
from app.resources import strings
from app.services.auth_token_header import AuthTokenHeader


async def get_current_user_authorizer(
        api_key: str = Security(AuthTokenHeader(name="Authorization")),
        settings: AppSettings = Depends(get_app_settings),
) -> User:
    headers = {
        "Content-Type": "application/json",
    }

    async with AsyncClient(base_url=settings.auth_service, headers=headers) as client:
        try:
            response = await client.get("/users", headers={"Authorization": api_key})
        except ConnectError as exception:
            logger.error(exception)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=strings.AUTHENTICATION_SERVER_UNAVAILABLE
            ) from exception

    response_wrapper = WrapperResponse(**response.json())
    if response_wrapper.success:
        user_response = UserResponse(**response_wrapper.payload)
        return user_response.user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=strings.MALFORMED_PAYLOAD)
