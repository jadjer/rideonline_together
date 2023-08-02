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

import pytest
import pytest_asyncio

from fastapi import FastAPI
from httpx import AsyncClient
from neo4j import AsyncDriver, AsyncSession, AsyncTransaction

from app.core.settings.app import AppSettings
from app.models.domain.user import User


@pytest.fixture
def settings() -> AppSettings:
    from app.core.config import get_app_settings
    return get_app_settings()


@pytest.fixture
def app() -> FastAPI:
    from app.app import get_application
    return get_application()


@pytest.fixture
def driver(settings: AppSettings) -> AsyncDriver:
    from neo4j import AsyncGraphDatabase

    driver: AsyncDriver = AsyncGraphDatabase.driver(
        settings.get_database_url,
        auth=(
            settings.database_user,
            settings.database_pass
        )
    )

    return driver


@pytest_asyncio.fixture
async def session(driver: AsyncDriver):
    session: AsyncSession = driver.session()
    transaction: AsyncTransaction = await session.begin_transaction()

    try:
        yield transaction

    finally:
        await transaction.rollback()
        await session.close()


@pytest.fixture
def initialized_app(app: FastAPI, session) -> FastAPI:
    app.state.session = session
    return app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(
            app=app,
            base_url="http://localhost:12345",
            headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def authorization_prefix(settings: AppSettings) -> str:
    return settings.jwt_token_prefix


@pytest.fixture
def token(settings: AppSettings, test_user: User) -> str:
    from app.services.token import create_access_token_for_user

    return create_access_token_for_user(
        test_user.id, test_user.username, test_user.phone, settings.secret_key.get_secret_value()
    )


@pytest.fixture
def authorized_client(client: AsyncClient, authorization_prefix: str, token: str) -> AsyncClient:
    client.headers = {"Authorization": f"{authorization_prefix} {token}", **client.headers}
    return client
