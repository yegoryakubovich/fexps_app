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
from flet_core import Row

from fexps_api_client.utils import ApiException

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AdminBaseView
from app.utils import Error


class TimezoneCreateView(AdminBaseView):
    route = '/admin/timezone/create'
    tf_deviation: TextField
    tf_id_str: TextField

    async def build(self):
        self.tf_id_str = TextField(
            label=await self.client.session.gtv(key='key'),
        )
        self.tf_deviation = TextField(
            label=await self.client.session.gtv(key='deviation'),
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_timezone_create_view_title'),
            main_section_controls=[
                self.tf_id_str,
                self.tf_deviation,
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='create'),
                                size=16,
                            ),
                            on_click=self.create_timezone,
                            expand=True,
                        ),
                    ],
                ),
            ],
         )

    async def create_timezone(self, _):
        await self.set_type(loading=True)
        fields = [(self.tf_id_str, 1, 16, False), (self.tf_deviation, 1, 16, True)]
        for field, min_len, max_len, check_int in fields:
            if not await Error.check_field(self, field, check_int=check_int, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        try:
            await self.client.session.api.admin.timezones.create(
                id_str=self.tf_id_str.value,
                deviation=self.tf_deviation.value,
            )
            await self.set_type(loading=False)
            await self.client.change_view(go_back=True, with_restart=True, delete_current=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
