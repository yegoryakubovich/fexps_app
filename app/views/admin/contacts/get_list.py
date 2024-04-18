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


from functools import partial

from flet_core import Text, ScrollMode, colors

from app.controls.information.card import Card
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from .create import ContactCreateView
from .get import ContactView


class ContactsListView(AdminBaseView):
    route = '/admin/contacts/list/get'
    contacts = list[dict]

    async def construct(self):
        await self.set_type(loading=True)
        self.contacts = await self.client.session.api.client.contacts.get_list()
        await self.set_type(loading=False)
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_contacts_get_list_view_title'),
            on_create_click=self.contact_create,
            main_section_controls=[
                Card(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key=contact.name_text),
                            size=18,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                    on_click=partial(self.contact_view, contact.id),
                    color=colors.PRIMARY_CONTAINER,
                )
                for contact in self.contacts
            ],
        )

    async def contact_create(self, _):
        await self.client.change_view(view=ContactCreateView())

    async def contact_view(self, contact_id: int, _):
        await self.client.change_view(view=ContactView(contact_id=contact_id))
