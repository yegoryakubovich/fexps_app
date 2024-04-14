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
import logging
from functools import partial

from flet_core import TextField, Row, Image, colors, ScrollMode

from app.controls.button import StandardButton
from app.controls.layout import AdminBaseView
from app.utils import Icons


class AccountContactView(AdminBaseView):
    route = '/admin/account/contact/get'
    contacts = list[dict]
    accounts_contacts = list[dict]
    accounts_contacts_dict: dict

    def __init__(self, account_id: int):
        super().__init__()
        self.account_id = account_id

    def reform_to_dict(self):
        for account_contact in self.accounts_contacts:
            self.accounts_contacts_dict[account_contact.contact_id] = account_contact.value

    async def build(self):
        self.accounts_contacts_dict = {}
        await self.set_type(loading=True)
        self.contacts = await self.client.session.api.client.contacts.get_list()
        self.accounts_contacts = await self.client.session.api.client.accounts.contacts.get_list()
        self.reform_to_dict()
        await self.set_type(loading=False)
        contact_controls = []
        self.scroll = ScrollMode.AUTO
        for contact in self.contacts:
            logging.critical(contact)
            contact_controls += [
                Row(
                    controls=[
                        TextField(
                            label=await self.client.session.gtv(key=contact.name_text),
                            value=self.accounts_contacts_dict.get(contact.id),
                            disabled=True,
                            expand=True,
                        ),
                        StandardButton(
                            content=Image(src=Icons.COPY, width=24, color=colors.ON_BACKGROUND),
                            on_click=partial(self.copy_to_clipboard, self.accounts_contacts_dict.get(contact.id)),
                            bgcolor=colors.BACKGROUND,
                        )
                    ]
                ),
            ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='account_contact_title'),
            main_section_controls=[
                *contact_controls,
            ],
        )

    async def copy_to_clipboard(self, data: str, _):
        if not data:
            return
        await self.client.page.set_clipboard_async(data)
