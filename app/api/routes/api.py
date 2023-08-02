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

from fastapi import APIRouter

from . import events, users_location, vehicle_location

router = APIRouter()

router.include_router(events.router, tags=["Events"], prefix="/events")
router.include_router(users_location.router, tags=["Users Location"], prefix="/users/location")
router.include_router(vehicle_location.router, tags=["Vehicles Location"], prefix="/vehicles/location")
