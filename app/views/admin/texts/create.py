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
from app.utils import Fonts, Error
from .get import TextView


class TextCreateView(AdminBaseView):
    route = '/admin/text/create'
    tf_value_default: TextField
    tf_key: TextField

    async def build(self):
        self.tf_key = TextField(
            label=await self.client.session.gtv(key='key'),
        )
        self.tf_value_default = TextField(
            label=await self.client.session.gtv(key='value_default'),
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_text_create_view_title'),
            main_section_controls=[
                self.tf_key,
                self.tf_value_default,
                Row(
                   controls=[
                       StandardButton(
                           content=Text(
                               value=await self.client.session.gtv(key='create'),
                               size=16,
                           ),
                           on_click=self.create_text,
                           expand=True,
                       ),
                   ],
                ),
            ],
         )

    async def create_text(self, _):
        await self.set_type(loading=True)
        fields = [(self.tf_key, 2, 128), (self.tf_value_default, 1, 1024)]
        for field, min_len, max_len in fields:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        try:
            key = await self.client.session.api.admin.texts.create(
                value_default=self.tf_value_default.value,
                key=self.tf_key.value,
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            await self.client.change_view(view=TextView(key=key), delete_current=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
