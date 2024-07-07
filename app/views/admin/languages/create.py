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


from flet_core import Row, ScrollMode

from config import settings
from fexps_api_client.utils import ApiException

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AdminBaseView
from app.utils.error import Error


class LanguageCreateView(AdminBaseView):
    route = '/admin/language/create'
    tf_name: TextField
    tf_id_str: TextField

    async def construct(self):
        self.tf_id_str, self.tf_name = [
            TextField(
                label=await self.client.session.gtv(key=key),
            )
            for key in ['key', 'name']
        ]
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_language_create_view_title'),
            main_section_controls=[
                self.tf_id_str,
                self.tf_name,
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='create'),
                                size=settings.get_font_size(multiple=1.5),
                            ),
                            on_click=self.create_language,
                            expand=True,
                        ),
                    ],
                ),
            ],
         )

    async def create_language(self, _):
        await self.set_type(loading=True)
        fields = [(self.tf_id_str, 1, 16), (self.tf_name, 1, 32)]
        for field, min_len, max_len in fields:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        try:
            await self.client.session.api.admin.languages.create(
                id_str=self.tf_id_str.value,
                name=self.tf_name.value,
            )
            await self.set_type(loading=False)
            await self.client.change_view(go_back=True, with_restart=True, delete_current=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
