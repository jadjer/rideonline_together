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

from datetime import datetime, timedelta

from jose import JWTError, jwt
from pydantic import ValidationError

from app.models.schemas.jwt import JWTUser

JWT_ACCESS_SUBJECT = "access"
JWT_REFRESH_SUBJECT = "refresh"
ALGORITHM = "RS512"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 365


def get_user_id_from_access_token(access_token: str, secret_key: str) -> int | None:
    try:
        token_date = jwt.decode(access_token, secret_key, algorithms=[ALGORITHM], subject=JWT_ACCESS_SUBJECT)
        user_data = JWTUser(**token_date)
    except JWTError:
        return None
    except ValidationError:
        return None
    except ValueError:
        return None

    user_id = user_data.user_id
    return user_id


def get_user_id_from_refresh_token(access_token: str, refresh_token: str, secret_key: str) -> int | None:
    try:
        token_date = jwt.decode(refresh_token, secret_key, algorithms=[ALGORITHM], subject=JWT_REFRESH_SUBJECT, access_token=access_token)
        user_data = JWTUser(**token_date)
    except JWTError:
        return None
    except ValidationError:
        return None
    except ValueError:
        return None

    user_id = user_data.user_id

    return user_id
