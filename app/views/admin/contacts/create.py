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

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AdminBaseView
from app.utils import Error
from fexps_api_client.utils import ApiException
from .get import ContactView


class ContactCreateView(AdminBaseView):
    route = '/admin/contacts/create'
    tf_name: TextField

    async def construct(self):
        self.tf_name = TextField(
            label=await self.client.session.gtv(key='name'),
        )
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_currency_create_view_title'),
            main_section_controls=[
                self.tf_name,
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='create'),
                                size=16,
                            ),
                            on_click=self.create_currency,
                            expand=True,
                        ),
                    ],
                ),
            ],
        )

    async def create_currency(self, _):
        await self.set_type(loading=True)
        for field, min_len, max_len in [(self.tf_name, 1, 128)]:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        try:
            id_ = await self.client.session.api.admin.contacts.create(
                name=self.tf_name.value,
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            await self.client.change_view(view=ContactView(contact_id=id_), delete_current=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
