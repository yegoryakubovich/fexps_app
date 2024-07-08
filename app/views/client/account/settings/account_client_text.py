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
from config import settings
from fexps_api_client.utils import ApiException


class AccountSettingsAccountClientTextView(ClientBaseView):
    route = '/client/account/client/text'

    clients_texts = list[dict]
    accounts_clients_texts = list[dict]

    dict_clients_texts_db: dict
    dict_clients_texts: dict
    dict_accounts_clients_texts: dict

    def reform_to_dict(self):
        for account_client_text in self.accounts_clients_texts:
            self.dict_clients_texts_db[account_client_text.client_text_id] = account_client_text.value
            self.dict_clients_texts[account_client_text.client_text_id] = account_client_text.value
            self.dict_accounts_clients_texts[account_client_text.client_text_id] = account_client_text.id

    async def construct(self):
        self.dict_clients_texts_db = {}
        self.dict_clients_texts = {}
        self.dict_accounts_clients_texts = {}
        await self.set_type(loading=True)
        self.clients_texts = await self.client.session.api.client.clients_texts.get_list()
        self.accounts_clients_texts = await self.client.session.api.client.accounts.clients_texts.get_list()
        self.reform_to_dict()
        await self.set_type(loading=False)
        client_text_controls = [
            TextField(
                label=await self.client.session.gtv(key=client_text.name_text),
                multiline=True,
                value=self.dict_clients_texts_db.get(client_text.id),
                on_change=partial(self.change_client_text, client_text.id),
            )
            for client_text in self.clients_texts
        ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='account_settings_account_client_text'),
            with_expand=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=client_text_controls,
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
                                    size=settings.get_font_size(multiple=1.5),
                                ),
                                on_click=self.update_account_client_text,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
            ],
        )

    async def change_client_text(self, client_text_id: int, event: ControlEvent):
        self.dict_clients_texts[client_text_id] = event.data
        if not self.dict_clients_texts[client_text_id]:
            del self.dict_clients_texts[client_text_id]

    async def update_account_client_text(self, _):
        await self.set_type(loading=True)
        try:
            for client_text_id in self.dict_clients_texts:
                if not self.dict_clients_texts.get(client_text_id):
                    if self.dict_accounts_clients_texts.get(client_text_id):
                        await self.client.session.api.client.accounts.clients_texts.delete(
                            id_=self.dict_accounts_clients_texts[client_text_id],
                        )
                    continue
                if self.dict_accounts_clients_texts.get(client_text_id) is None:
                    await self.client.session.api.client.accounts.clients_texts.create(
                        client_text_id=client_text_id,
                        value=self.dict_clients_texts[client_text_id],
                    )
                    continue
                if self.dict_clients_texts[client_text_id] == self.dict_clients_texts_db[client_text_id]:
                    continue
                await self.client.session.api.client.accounts.clients_texts.update(
                    id_=self.dict_accounts_clients_texts[client_text_id],
                    value=self.dict_clients_texts[client_text_id],
                )
            await self.set_type(loading=False)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
