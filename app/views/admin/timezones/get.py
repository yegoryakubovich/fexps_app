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


from app.controls.button import StandardButton, StandardButton
from app.controls.information import Text
from app.controls.layout import AdminBaseView


class TimezoneView(AdminBaseView):
    route = '/admin/timezone/get'
    timezone = dict

    def __init__(self, timezone_id_str):
        super().__init__()
        self.timezone_id_str = timezone_id_str

    async def construct(self):
        await self.set_type(loading=True)
        self.timezone = await self.client.session.api.client.timezones.get(
            id_str=self.timezone_id_str
        )
        await self.set_type(loading=False)

        self.controls = await self.get_controls(
            title=self.timezone['id_str'],
            main_section_controls=[
                StandardButton(
                    content=Text(
                        value=await self.client.session.gtv(key='delete'),
                    ),
                    on_click=self.delete_timezone,
                    expand=True,
                ),
            ],
         )

    async def delete_timezone(self, _):
        await self.client.session.api.admin.timezones.delete(
            id_str=self.timezone_id_str,
        )
        await self.client.change_view(go_back=True, with_restart=True)
