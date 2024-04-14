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
from app.controls.layout import AdminBaseView


class ContactView(AdminBaseView):
    route = '/admin/contacts/get'
    contact = dict

    def __init__(self, contact_id):
        super().__init__()
        self.contact_id = contact_id

    async def build(self):
        await self.set_type(loading=True)
        self.contact = await self.client.session.api.client.contacts.get(id_=self.contact_id)
        await self.set_type(loading=False)
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key=self.contact.name_text),
            main_section_controls=[
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='delete'),
                            ),
                            on_click=self.contact_delete,
                            expand=True,
                        ),
                    ]
                ),
            ],
        )

    async def contact_delete(self, _):
        await self.client.session.api.admin.contacts.delete(id_=self.contact_id)
        await self.client.change_view(go_back=True, with_restart=True, delete_current=True)
