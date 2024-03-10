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
from typing import Optional

from flet_core import Column, Container, ScrollMode, padding, colors, KeyboardType
from flet_core.dropdown import Option

from app.controls.button import FilledButton
from app.controls.information import Text
from app.controls.input import TextField, Dropdown
from app.controls.layout import ClientBaseView
from app.utils import Fonts
from fexps_api_client.utils import ApiException


class RequestTypes:
    input = 'input'
    output = 'output'
    all = 'all'


def find_wallet_option(options: list[Option], id_: int) -> Option:
    for option in options:
        if option.key == id_:
            return option
    return options[0]


class RequestCreateView(ClientBaseView):
    route = '/client/requisite/create'
    controls_container: Container
    optional: Column
    currencies: Column
    methods = dict

    dd_type: Dropdown = None
    dd_wallet: Dropdown = None
    dd_input_currency: Dropdown = None
    dd_output_currency: Dropdown = None
    dd_input_method: Dropdown = None
    tf_input_currency_value: TextField = None
    tf_input_value: TextField = None
    dd_output_requisite_data: Dropdown = None
    tf_output_currency_value: TextField = None
    tf_output_value: TextField = None

    def __init__(self, current_wallet, **kwargs):
        super().__init__(**kwargs)
        self.current_wallet = current_wallet

    async def build(self):
        # self.client.session.account
        self.methods = await self.client.session.api.client.methods.get_list()

        type_options = [Option(
            text=await self.client.session.gtv(key=f'request_type_{type_}'),
            key=type_,
        ) for type_ in [RequestTypes.input, RequestTypes.output, RequestTypes.all]]
        wallets_options = [Option(
            key=wallet.id, text=f'#{wallet.id} - {wallet.name}'
        ) for wallet in await self.client.session.api.client.wallets.get_list()]
        currency_options = [Option(
            text=currency.id_str.upper(),
            key=currency.id_str,
        ) for currency in await self.client.session.api.client.currencies.get_list()]

        self.dd_type = Dropdown(
            label=await self.client.session.gtv(key='type'),
            options=type_options,
            on_change=self.change_type_or_currency,
        )
        self.dd_wallet = Dropdown(
            label=await self.client.session.gtv(key='wallet'),
            options=wallets_options,
            value=wallets_options[0].key,
        )
        self.dd_input_currency = Dropdown(
            label=await self.client.session.gtv(key='input_currency'),
            options=currency_options,
            on_change=self.change_type_or_currency,
        )
        self.dd_output_currency = Dropdown(
            label=await self.client.session.gtv(key='output_currency'),
            options=currency_options,
            on_change=self.change_type_or_currency,
        )

        self.currencies = Column(controls=[])
        self.optional = Column(controls=[])

        self.controls_container = Container(
            content=Column(
                controls=[
                    self.dd_type,
                    self.dd_wallet,
                    self.currencies,
                    self.optional,
                    FilledButton(
                        text=await self.client.session.gtv(key='next'),
                        on_click=self.switch_tf,
                    )
                ],
                spacing=10,
            ),
            padding=padding.only(bottom=15),
        )
        controls = [
            self.controls_container
        ]
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='request_create'),
            main_section_controls=controls,
        )

    async def change_type_or_currency(self, _):
        async def get_input_method():
            input_method_options = []
            for method in self.methods:
                if method.currency.lower() != self.dd_input_currency.value.lower():
                    continue
                name = await self.client.session.gtv(key=method.name_text)
                input_method_options.append(Option(
                    text=f'{name} ({method.id})',
                    key=method.id,
                ))
            return Dropdown(
                label=await self.client.session.gtv(key='input_method'),
                options=input_method_options,
            )

        async def get_output_requisite_data():
            requisites_datas = await self.client.session.api.client.requisite_data.get_list()
            output_requisite_data_options = []
            for requisite_data in requisites_datas:
                if requisite_data.currency.lower() != self.dd_output_currency.value.lower():
                    continue
                output_requisite_data_options.append(Option(
                    text=f'{requisite_data.name}',
                    key=requisite_data.id,
                ))
            return Dropdown(
                label=await self.client.session.gtv(key='output_requisite_data'),
                options=output_requisite_data_options,
            )

        if not self.dd_type.value:
            self.currencies.controls = []
            self.optional.controls = []
            await self.update_async()
            return
        if self.dd_type.value == RequestTypes.input:
            self.currencies.controls = [self.dd_input_currency]
            if not self.dd_input_currency.value:
                self.optional.controls = []
                await self.update_async()
                return
            self.dd_input_method = await get_input_method()
            self.tf_input_currency_value = TextField(
                label=await self.client.session.gtv(key='input_currency_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.tf_input_value = TextField(
                label=await self.client.session.gtv(key='input_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.optional.controls = [
                self.dd_input_method,
                self.tf_input_currency_value,
                self.tf_input_value,
            ]
        elif self.dd_type.value == RequestTypes.output:
            self.currencies.controls = [self.dd_output_currency]
            if not self.dd_output_currency.value:
                self.optional.controls = []
                await self.update_async()
                return
            self.dd_output_requisite_data = await get_output_requisite_data()
            self.tf_output_currency_value = TextField(
                label=await self.client.session.gtv(key='output_currency_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.tf_output_value = TextField(
                label=await self.client.session.gtv(key='output_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.optional.controls = [
                self.dd_output_requisite_data,
                self.tf_output_currency_value,
                self.tf_output_value,
            ]
        elif self.dd_type.value == RequestTypes.all:
            self.currencies.controls = [self.dd_input_currency, self.dd_output_currency]
            if not self.dd_input_currency.value or not self.dd_output_currency.value:
                self.optional.controls = []
                await self.update_async()
                return
            self.dd_input_method = await get_input_method()
            self.dd_output_requisite_data = await get_output_requisite_data()
            self.tf_input_currency_value = TextField(
                label=await self.client.session.gtv(key='input_currency_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.tf_output_currency_value = TextField(
                label=await self.client.session.gtv(key='output_currency_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.optional.controls = [
                self.dd_input_method,
                self.dd_output_requisite_data,
                self.tf_input_currency_value,
                self.tf_output_currency_value,
            ]
        await self.update_async()

    async def go_back(self, _):
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)

    async def switch_tf(self, _):
        def fix_value(value: Optional[str], decimal: int):
            if not value:
                return
            value = value.replace(',', '.')
            value = float(value)
            return int(value * decimal)

        await self.set_type(loading=True)
        input_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_input_currency.value)
        output_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_output_currency.value)
        # Input values
        input_currency_value = fix_value(
            value=self.tf_input_currency_value.value, decimal=10 ** input_currency.decimal,
        ) if self.tf_input_currency_value else None
        input_value = fix_value(
            value=self.tf_input_value.value, decimal=10 ** input_currency.decimal,
        ) if self.tf_input_value else None
        # Output values
        output_currency_value = fix_value(
            value=self.tf_output_currency_value.value, decimal=10 ** output_currency.decimal,
        ) if self.tf_output_currency_value else None
        output_value = fix_value(
            value=self.tf_output_value.value, decimal=10 ** output_currency.decimal,
        ) if self.tf_output_value else None

        try:
            await self.client.session.api.client.request.create(
                wallet_id=self.dd_wallet.value if self.dd_wallet else None,
                type_=self.dd_type.value if self.dd_type else None,
                input_method_id=self.dd_input_method.value if self.dd_input_method else None,
                input_currency_value=input_currency_value,
                input_value=input_value,
                output_requisite_data_id=self.dd_output_requisite_data.value if self.dd_output_requisite_data else None,
                output_currency_value=output_currency_value,
                output_value=output_value,
            )
            await self.set_type(loading=False)
        except ApiException as exception:
            await self.set_type(loading=False)
            logging.critical(exception.message)
            return await self.client.session.error(exception=exception)
        self.controls_container = Container(
            content=Column(
                [
                    Text(
                        value=await self.client.session.gtv(key='request_create_success'),
                        size=15,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_BACKGROUND,
                    ),
                    FilledButton(
                        text=await self.client.session.gtv(key='go_back'),
                        on_click=self.go_back,
                    )
                ]
            )
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='request_create'),
            main_section_controls=[self.controls_container],
        )
        await self.update_async()
