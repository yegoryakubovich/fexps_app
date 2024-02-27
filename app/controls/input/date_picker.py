#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from datetime import datetime

from flet_core import DatePicker as DatePickerFlet


class DatePicker(DatePickerFlet):
    def __init__(self):
        super().__init__()

    async def open_(
            self,
            on_select=None,
            on_dismiss=None,
            date_from: datetime = datetime(year=2024, month=1, day=1),
            date_to: datetime = datetime(year=2025, month=1, day=1),
    ):
        self.on_change = on_select
        self.on_dismiss = on_dismiss
        self.first_date = date_from
        self.last_date = date_to
        await self.pick_date_async()
