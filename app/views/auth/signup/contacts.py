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

from flet_core import Column, Row, TextField, ControlEvent, Container, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import AuthView
from app.views.auth.signup import AgreementRegistrationView


class ContactRegistrationView(AuthView):
    contacts = list[dict]
    result: dict

    async def construct(self):
        self.result = {}
        await self.set_type(loading=True)
        self.contacts = await self.client.session.api.client.contacts.get_list()
        await self.set_type(loading=False)
        contact_controls = []
        for contact in self.contacts:
            contact_controls += [
                TextField(
                    label=await self.client.session.gtv(key=contact.name_text),
                    on_change=partial(self.change_contact, contact.id),
                ),
            ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='registration_account_create_view_title'),
            with_expand=True,
            controls=[
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
                                    value=await self.client.session.gtv(key='next_step'),
                                ),
                                on_click=self.change_view,
                                expand=True,
                            ),
                        ],
                    ),
                ),
            ],
        )

    async def change_contact(self, contact_id: int, event: ControlEvent):
        self.result[contact_id] = event.data

    async def change_view(self, _):
        self.client.session.registration.contacts = self.result
        await self.client.change_view(view=AgreementRegistrationView(), delete_current=True)
