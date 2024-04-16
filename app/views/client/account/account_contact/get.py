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

from _ctypes import alignment
from flet_core import Row, Column, ControlEvent, ScrollMode, Container, alignment

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from fexps_api_client.utils import ApiException


class AccountContactView(ClientBaseView):
    route = '/client/account/contact/get'
    contacts = list[dict]
    accounts_contacts = list[dict]
    result_dict: dict

    def reform_to_dict(self):
        for account_contact in self.accounts_contacts:
            self.result_dict['contacts_db'][account_contact.contact_id] = account_contact.value
            self.result_dict['contacts'][account_contact.contact_id] = account_contact.value
            self.result_dict['contacts_account_contacts'][account_contact.contact_id] = account_contact.id

    async def build(self):
        self.result_dict = {
            'contacts_db': {},
            'contacts': {},
            'contacts_account_contacts': {},
        }
        await self.set_type(loading=True)
        self.contacts = await self.client.session.api.client.contacts.get_list()
        self.accounts_contacts = await self.client.session.api.client.accounts.contacts.get_list()
        self.reform_to_dict()
        await self.set_type(loading=False)
        contact_controls = []
        for contact in self.contacts:
            contact_controls += [
                TextField(
                    label=await self.client.session.gtv(key=contact.name_text),
                    value=self.result_dict['contacts_db'].get(contact.id),
                    on_change=partial(self.change_contact, contact.id),
                )
            ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='account_contact_title'),
            with_expand=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=contact_controls,
                        scroll=ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='save'),
                                ),
                                on_click=self.update_account_contact,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                )
            ],
        )

    async def change_contact(self, contact_id: int, _: ControlEvent):
        self.result_dict['contacts'][contact_id] = _.data

    async def update_account_contact(self, _):
        await self.set_type(loading=True)
        try:
            for contact_id in self.result_dict['contacts']:
                if not self.result_dict['contacts'].get(contact_id):
                    if self.result_dict['contacts_account_contacts'].get(contact_id):
                        await self.client.session.api.client.accounts.contacts.delete(
                            id_=self.result_dict['contacts_account_contacts'][contact_id],
                        )
                    continue
                if self.result_dict['contacts_account_contacts'].get(contact_id) is None:
                    await self.client.session.api.client.accounts.contacts.create(
                        contact_id=contact_id,
                        value=self.result_dict['contacts'][contact_id],
                    )
                    continue
                if self.result_dict['contacts'][contact_id] == self.result_dict['contacts_db'][contact_id]:
                    continue
                await self.client.session.api.client.accounts.contacts.update(
                    id_=self.result_dict['contacts_account_contacts'][contact_id],
                    value=self.result_dict['contacts'][contact_id],
                )
            await self.set_type(loading=False)
            await self.build()
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
