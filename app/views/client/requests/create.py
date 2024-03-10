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

from flet_core import Column, Container, ScrollMode, padding, colors, KeyboardType, ControlEvent
from flet_core.dropdown import Option

from app.controls.button import FilledButton
from app.controls.information import Text
from app.controls.input import TextField, Dropdown
from app.controls.layout import ClientBaseView
from app.utils import Fonts
from fexps_api_client import FexpsApiClient
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

    dd_type: Dropdown
    dd_wallet: Dropdown
    dd_currency: Dropdown
    dd_input_method: Dropdown
    tf_input_currency_value: TextField
    tf_input_value: TextField
    dd_output_requisite_data: Dropdown
    tf_output_currency_value: TextField
    tf_output_value: TextField

    def __init__(self, current_wallet, **kwargs):
        super().__init__(**kwargs)
        self.current_wallet = current_wallet

    async def get_type_dd(self, options: list[Option]) -> Dropdown:
        return Dropdown(
            label=await self.client.session.gtv(key='type'),
            options=options,
            value=options[0],
            on_change=self.change_type,
        )

    async def get_wallet_dd(self, options: list[Option]) -> Dropdown:
        return Dropdown(
            label=await self.client.session.gtv(key='wallet'),
            options=options,
            value=find_wallet_option(options=options, id_=self.current_wallet.id).key,
        )

    async def get_currency_dd(self, options: list[Option]) -> Dropdown:
        return Dropdown(
            label=await self.client.session.gtv(key='currency'),
            options=options,
            value=options[0].key if options else None,
        )

    async def get_input_method_dd(self, options: list[Option]) -> Dropdown:
        return Dropdown(
            label=await self.client.session.gtv(key='input_method'),
            options=options,
            value=options[0].key if options else None,
        )

    async def get_output_requisite_data_dd(self, options: list[Option]) -> Dropdown:
        return Dropdown(
            label=await self.client.session.gtv(key='output_requisite_data'),
            options=options,
            value=options[0].key if options else None,
        )

    async def build(self):
        # self.client.session.account

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

        self.dd_type = await self.get_type_dd(options=type_options)
        self.dd_wallet = await self.get_wallet_dd(options=wallets_options)
        self.dd_currency = await self.get_currency_dd(options=currency_options)

        self.optional = Column(controls=[])

        self.controls_container = Container(
            content=Column(
                controls=[
                    self.dd_type,
                    self.dd_wallet,
                    self.dd_currency,
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

    async def change_type(self, event: ControlEvent):
        if event.data == RequestTypes.input:
            input_method_options = []
            self.dd_input_method = await self.get_input_method_dd(options=input_method_options)
            self.tf_input_currency_value = TextField(
                label=await self.client.session.gtv(key='request_create_input_currency_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.tf_input_value = TextField(
                label=await self.client.session.gtv(key='request_create_input_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.optional.controls = [
                self.dd_input_method,
                self.tf_input_currency_value,
                self.tf_input_value,
            ]
        elif event.data == RequestTypes.output:
            output_requisite_data_options = []
            self.dd_output_requisite_data = await self.get_output_requisite_data_dd(
                options=output_requisite_data_options,
            )
            self.tf_output_currency_value = TextField(
                label=await self.client.session.gtv(key='request_create_output_currency_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.tf_output_value = TextField(
                label=await self.client.session.gtv(key='request_create_output_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.optional.controls = [
                self.dd_output_requisite_data,
                self.tf_output_currency_value,
                self.tf_output_value,
            ]
        elif event.data == RequestTypes.all:
            input_method_options = []
            output_requisite_data_options = []
            self.dd_input_method = await self.get_input_method_dd(options=input_method_options)
            self.dd_output_requisite_data = await self.get_output_requisite_data_dd(
                options=output_requisite_data_options,
            )
            self.tf_input_currency_value = TextField(
                label=await self.client.session.gtv(key='request_create_input_currency_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.tf_output_currency_value = TextField(
                label=await self.client.session.gtv(key='request_create_output_currency_value'),
                keyboard_type=KeyboardType.NUMBER,
            )
            self.optional.controls = [
                self.dd_input_method,
                self.dd_output_requisite_data,
                self.tf_input_currency_value,
                self.tf_output_currency_value,
            ]
        await self.update_async()

    async def change_currency(self, event: ControlEvent):
        method_options = []
        logging.critical(event.data)
        for method in self.methods:
            if method.currency != event.data:
                continue
            method_options.append(Option(
                text=await self.client.session.gtv(key=method.name_text),
                key=method.id,
            ))
        logging.critical(method_options)
        self.dd_method.options = method_options
        await self.update_async()

    async def go_back(self, _):
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)

    async def switch_tf(self, _):
        self.wallet_to_id_tf.error_text = None
        self.value_tf.error_text = None
        try:
            await self.client.session.api.client.transfers.create(
                wallet_from_id=self.client.session.current_wallet.id,
                wallet_to_id=int(self.wallet_to_id_tf.value),
                value=int(self.value_tf.value),
            )
        except ApiException as e:
            if e.code in [1000, ]:
                self.wallet_to_id_tf.error_text = e.message
            elif e.code in [6002, ]:
                self.value_tf.error_text = e.message
            else:
                self.value_tf.error_text = f'{e.code} - {e.message}'
            await self.update_async()
            return
        self.controls_container = Container(
            content=Column(
                [
                    Text(
                        value=await self.client.session.gtv(key='payment_success'),
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
            title=await self.client.session.gtv(key='change_password'),
            main_section_controls=[self.controls_container],
        )
        await self.update_async()
