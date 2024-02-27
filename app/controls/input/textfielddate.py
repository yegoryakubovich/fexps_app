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


from app.controls.input import TextField


class TextFieldDate(TextField):
    def __init__(self, label, client, **kwargs):
        super().__init__(label=label, **kwargs)
        self.client = client
        self.disabled = False
        self.on_focus = self.open_datepicker

    async def close_datepicker(self, _):
        self.disabled = False
        await self.update_async()

    async def open_datepicker(self, _):
        await self.client.session.datepicker.open_(
            on_select=self.select_datepicker,
            on_dismiss=self.close_datepicker,
        )
        self.disabled = True
        await self.update_async()

    async def select_datepicker(self, _):
        self.disabled = False
        await self.update_async()
        selected_date = self.client.session.datepicker.value
        date_string = selected_date.strftime("%Y-%m-%d")
        self.value = date_string
        await self.update_async()
