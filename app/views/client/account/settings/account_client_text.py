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
from flet_core import Row, Column, ControlEvent, ScrollMode, Container, alignment, Divider, colors

from app.controls.button import StandardButton
from app.controls.information import Text, SubTitle
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils.constants.client_text import ClientTextTypes
from config import settings
from fexps_api_client.utils import ApiException


class AccountSettingsAccountClientTextView(ClientBaseView):
    route = '/client/account/client/text'

    clients_texts = list[dict]
    accounts_cts = list[dict]

    result: dict

    async def construct(self):
        await self.set_type(loading=True)
        self.clients_texts = await self.client.session.api.client.clients_texts.get_list()
        self.accounts_cts = await self.client.session.api.client.accounts.clients_texts.get_list()
        await self.set_type(loading=False)
        self.result = {}
        for account_ct in self.accounts_cts:
            self.result[account_ct.client_text_id] = account_ct.value
        request_all_controls = [
            SubTitle(
                value=await self.client.session.gtv(
                    key=f'account_settings_account_client_text_{ClientTextTypes.REQUEST_ALL}',
                ),
            ),
        ]
        request_input_controls = [
            SubTitle(
                value=await self.client.session.gtv(
                    key=f'account_settings_account_client_text_{ClientTextTypes.REQUEST_INPUT}',
                ),
            ),
        ]
        request_output_controls = [
            SubTitle(
                value=await self.client.session.gtv(
                    key=f'account_settings_account_client_text_{ClientTextTypes.REQUEST_OUTPUT}',
                ),
            ),
        ]
        for client_text in self.clients_texts:
            if client_text.type == ClientTextTypes.REQUEST_INPUT:
                request_input_controls.append(
                    TextField(
                        label=await self.client.session.gtv(key=client_text.name_text),
                        multiline=True,
                        value=self.result.get(client_text.id),
                        on_change=partial(self.change_client_text, client_text.id),
                    )
                )
            elif client_text.type == ClientTextTypes.REQUEST_OUTPUT:
                request_output_controls.append(
                    TextField(
                        label=await self.client.session.gtv(key=client_text.name_text),
                        multiline=True,
                        value=self.result.get(client_text.id),
                        on_change=partial(self.change_client_text, client_text.id),
                    )
                )
            elif client_text.type == ClientTextTypes.REQUEST_ALL:
                request_all_controls.append(
                    TextField(
                        label=await self.client.session.gtv(key=client_text.name_text),
                        multiline=True,
                        value=self.result.get(client_text.id),
                        on_change=partial(self.change_client_text, client_text.id),
                    )
                )
        if len(request_all_controls) == 1:
            request_all_controls = []
        if len(request_input_controls) == 1:
            request_input_controls = []
        if len(request_output_controls) == 1:
            request_output_controls = []
        extra_information_controls = [
            SubTitle(
                value=await self.client.session.gtv(
                    key='account_settings_account_client_text_extra_information',
                ),
            ),
        ]
        extra_information_create_list = []
        for name in ['type', 'state', 'input_currency_value', 'input_value', 'output_value', 'output_currency_value']:
            extra_information_create_list.append(
                await self.client.session.gtv(key=f'account_settings_account_client_text_extra_information_{name}'),
            )
        extra_information_controls.append(
            TextField(
                label=await self.client.session.gtv(
                    key='account_settings_account_client_text_extra_information_create',
                ),
                value='\n'.join(extra_information_create_list),
                multiline=True,
                read_only=True,
            )
        )
        extra_information_other_list = []
        for name in [
            'name', 'type', 'state', 'commission', 'rate',
            'input_currency_value', 'input_rate', 'input_value',
            'output_value', 'output_rate', 'output_currency_value',
            'date', 'input_orders', 'output_orders',
        ]:
            extra_information_other_list.append(
                await self.client.session.gtv(key=f'account_settings_account_client_text_extra_information_{name}'),
            )
        extra_information_controls.append(
            TextField(
                label=await self.client.session.gtv(
                    key='account_settings_account_client_text_extra_information_other',
                ),
                value='\n'.join(extra_information_other_list),
                multiline=True,
                read_only=True,
            )
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='account_settings_account_client_text'),
            with_expand=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=[
                            *request_all_controls,
                            *request_input_controls,
                            *request_output_controls,
                            Divider(color=colors.ON_BACKGROUND),
                            *extra_information_controls,
                        ],
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
        self.result[client_text_id] = event.data
        if not event.data:
            self.result[client_text_id] = None

    async def update_account_client_text(self, _):
        await self.set_type(loading=True)
        accounts_cts_ids = {}
        for account_ct in self.accounts_cts:
            accounts_cts_ids[account_ct.client_text_id] = account_ct.id
        try:
            for client_text in self.clients_texts:
                value = self.result.get(client_text.id)
                if not value:
                    if not accounts_cts_ids.get(client_text.id):
                        continue
                    await self.client.session.api.client.accounts.clients_texts.delete(
                        id_=accounts_cts_ids[client_text.id],
                    )
                elif accounts_cts_ids.get(client_text.id):
                    await self.client.session.api.client.accounts.clients_texts.update(
                        id_=accounts_cts_ids[client_text.id],
                        value=value,
                    )
                else:
                    await self.client.session.api.client.accounts.clients_texts.create(
                        client_text_id=client_text.id,
                        value=value,
                    )
            await self.set_type(loading=False)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
