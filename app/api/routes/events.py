#  Copyright 2023 Pavel Suprunov
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

from fastapi import APIRouter, Depends, status, HTTPException

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.get_filter import get_events_filter
from app.api.dependencies.get_from_path import get_event_id_from_path
from app.api.dependencies.rabbitmq_client import get_rabbitmq_client
from app.database.repositories.event_repository import EventRepository
from app.models.domain.action import Action, ActionType
from app.models.domain.user import User
from app.models.schemas.event import EventsFilter, EventResponse, EventsResponse, EventCreate, EventUpdate
from app.models.schemas.wrapper import WrapperResponse
from app.rabbitmq_client.rabbitmq_client import RabbitmqClient
from app.resources import strings

router = APIRouter()


@router.post("", status_code=status.HTTP_200_OK, name="events:create-event")
async def create_event(
        request: EventCreate,
        user: User = Depends(get_current_user_authorizer),
        event_repository: EventRepository = Depends(get_repository(EventRepository)),
        rabbitmq_client: RabbitmqClient = Depends(get_rabbitmq_client),
) -> WrapperResponse:
    if await event_repository.get_event_by_title(request.title):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.EVENT_IS_EXISTS)

    event = await event_repository.create_event_by_user_id(user.id, **request.__dict__)
    if not event:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.EVENT_CREATE_ERROR)

    rabbitmq_client.set_action(
        Action(type=ActionType.EVENT_ADD)
    )

    return WrapperResponse(payload=EventResponse(event=event))


@router.get("", status_code=status.HTTP_200_OK, name="events:get-events-by-filter")
async def get_events_by_filter(
        events_filter: EventsFilter = Depends(get_events_filter),
        # user: User = Depends(get_current_user_authorizer),
        event_repository: EventRepository = Depends(get_repository(EventRepository)),
) -> WrapperResponse:
    events = await event_repository.get_events(events_filter.limit, events_filter.offset)

    return WrapperResponse(payload=EventsResponse(events=events))


@router.get("/{event_id}", status_code=status.HTTP_200_OK, name="events:get-event-by-id")
async def get_event_by_id(
        event_id: int = Depends(get_event_id_from_path),
        user: User = Depends(get_current_user_authorizer),
        event_repository: EventRepository = Depends(get_repository(EventRepository)),
) -> WrapperResponse:
    event = await event_repository.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.EVENT_DOES_NOT_EXIST)

    return WrapperResponse(payload=EventResponse(event=event))


@router.patch('/{event_id}', status_code=status.HTTP_200_OK, name="events:update-event-by-id")
async def update_event_by_id(
        request: EventUpdate,
        event_id: int = Depends(get_event_id_from_path),
        user: User = Depends(get_current_user_authorizer),
        event_repository: EventRepository = Depends(get_repository(EventRepository)),
        rabbitmq_client: RabbitmqClient = Depends(get_rabbitmq_client),
) -> WrapperResponse:
    if await event_repository.get_event_by_title(request.title):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.EVENT_IS_EXISTS)

    if not await event_repository.get_event_by_id(event_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.EVENT_DOES_NOT_EXIST)

    event = await event_repository.update_event_by_id(user.id, event_id, **request.__dict__)
    if not event:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.EVENT_CREATE_ERROR)

    rabbitmq_client.set_action(
        Action(type=ActionType.EVENT_UPDATE)
    )

    return WrapperResponse(payload=EventResponse(event=event))


@router.delete("/{event_id}", status_code=status.HTTP_200_OK, name="events:delete-event-by-id")
async def delete_event_by_id(
        event_id: int = Depends(get_event_id_from_path),
        user: User = Depends(get_current_user_authorizer),
        event_repository: EventRepository = Depends(get_repository(EventRepository)),
        rabbitmq_client: RabbitmqClient = Depends(get_rabbitmq_client),
) -> WrapperResponse:
    if not await event_repository.get_event_by_id(event_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.EVENT_DOES_NOT_EXIST)

    await event_repository.delete_event_by_id(user.id, event_id)

    rabbitmq_client.set_action(
        Action(type=ActionType.EVENT_DELETE)
    )

    return WrapperResponse()
