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

from flet_core import Column, Container, KeyboardType, Row, alignment, Control
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import SubTitle
from app.controls.input import TextField, Dropdown
from app.controls.layout import ClientBaseView
from app.utils.value import value_to_int
from app.views.client.requests.get import RequestView
from fexps_api_client.utils import ApiException


class RequestTypes:
    INPUT = 'input'
    OUTPUT = 'output'
    ALL = 'all'


class RequestCreateView(ClientBaseView):
    route = '/client/request/create'
    controls_container: Container
    optional: Column
    methods = dict
    currencies = list[dict]

    # input
    tf_input_value = TextField(value=None)
    dd_input_currency = Dropdown(value=None)
    dd_input_method = Dropdown(value=None)

    # output
    tf_output_value = TextField(value=None)
    dd_output_currency = Dropdown(value=None)
    dd_output_method = Dropdown(value=None)
    dd_output_requisite_data = Dropdown(value=None)

    """
    SEND
    """

    async def get_currency_options(self, exclude_currency: str = None) -> list[Option]:
        options = [Option(text='ECOIN', key='ecoin')] if exclude_currency != 'ecoin' else []
        for currency in self.currencies:
            if currency.id_str == exclude_currency:
                continue
            options.append(Option(text=currency.id_str.upper(), key=currency.id_str))
        return options

    async def get_method_options(self, currency: str) -> list[Option]:
        options = []
        for method in self.methods:
            if method.currency.upper() != currency.upper():
                continue
            options.append(Option(
                text=f'{await self.client.session.gtv(key=method.name_text)} ({method.id})',
                key=method.id,
            ))
        return options

    async def get_input(self) -> list[Control]:
        self.tf_input_value = TextField(
            label=await self.client.session.gtv(key='value'),
            keyboard_type=KeyboardType.NUMBER,
            expand=4
        )
        self.dd_input_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            options=await self.get_currency_options(),
            on_change=partial(self.change_currency, 'input'),
            expand=1,
        )
        self.dd_input_method = Dropdown(
            label=await self.client.session.gtv(key='request_create_input_method'),
            disabled=True,
        )
        return [
            SubTitle(value=await self.client.session.gtv(key='request_create_input')),
            Row(
                controls=[
                    self.tf_input_value,
                    self.dd_input_currency,
                ],
                spacing=16,
            ),
            self.dd_input_method,
        ]

    """
    RECEIVE
    """

    async def get_output(self) -> list[Control]:
        self.tf_output_value = TextField(
            label=await self.client.session.gtv(key='value'),
            keyboard_type=KeyboardType.NUMBER,
            expand=4
        )
        self.dd_output_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            options=await self.get_currency_options(),
            on_change=partial(self.change_currency, 'output'),
            expand=1,
        )
        self.dd_output_method = Dropdown(
            label=await self.client.session.gtv(key='request_create_output_method'),
            on_change=self.change_output_method,
            disabled=True,
        )
        self.dd_output_requisite_data = Dropdown(
            label=await self.client.session.gtv(key='request_create_output_requisite_data'),
            disabled=True,
        )
        return [
            SubTitle(value=await self.client.session.gtv(key='request_create_input')),
            Row(
                controls=[
                    self.tf_output_value,
                    self.dd_output_currency,
                ],
                spacing=16,
            ),
            self.dd_output_method,
            self.dd_output_requisite_data,
        ]

    async def build(self):
        await self.set_type(loading=True)
        self.methods = await self.client.session.api.client.methods.get_list()
        self.currencies = await self.client.session.api.client.currencies.get_list()
        await self.set_type(loading=False)
        self.controls = await self.get_controls(
            with_expand=True,
            title=await self.client.session.gtv(key='request_create_title'),
            main_section_controls=[
                *await self.get_input(),
                *await self.get_output(),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                text=await self.client.session.gtv(key='request_create_button'),
                                on_click=self.request_create,
                                expand=True,
                            )
                        ],
                    ),
                    expand=True,
                    alignment=alignment.bottom_center,
                ),
            ],
        )

    async def change_currency(self, type_: str, _):
        await self.set_type(loading=True)
        if type_ == 'input' and self.dd_input_currency.value:
            currency = self.dd_input_currency.value
            self.dd_input_method.disabled = False
            self.dd_input_method.options = await self.get_method_options(currency=currency)
            self.dd_output_currency.options = await self.get_currency_options(exclude_currency=currency)
        if type_ == 'output' and self.dd_output_currency.value:
            currency = self.dd_output_currency.value
            self.dd_output_method.disabled = False
            self.dd_output_method.options = await self.get_method_options(currency=currency)
            self.dd_input_currency.options = await self.get_currency_options(exclude_currency=currency)
        await self.set_type(loading=False)

    async def change_output_method(self, _):
        await self.set_type(loading=True)
        requisites_datas = await self.client.session.api.client.requisites_datas.get_list()
        options = []
        for requisite_data in requisites_datas:
            if int(requisite_data.method) != int(self.dd_output_method.value):
                continue
            options.append(Option(
                text=f'{requisite_data.name}',
                key=requisite_data.id,
            ))
        self.dd_output_requisite_data.disabled = False
        self.dd_output_requisite_data.options = options
        await self.set_type(loading=False)

    async def go_back(self, _):
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)

    async def request_create(self, _):
        if self.tf_input_value.value and self.tf_output_value.value:
            self.tf_output_value.error_text = await self.client.session.gtv(key='request_create_error_only_one_fields')
            await self.update_async()
            return
        if len(self.client.session.wallets) == 1:
            return await self.go_request_create(wallet_id=self.client.session.wallets[0]['id'])

    async def go_request_create(self, wallet_id: int):
        input_method_id, input_currency_value, input_value = None, None, None
        output_requisite_data_id, output_currency_value, output_value = None, None, None
        await self.set_type(loading=True)
        if self.dd_output_currency.value == 'ecoin':
            input_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_input_currency.value)
            type_ = RequestTypes.INPUT
            input_method_id = self.dd_input_method.value
            input_currency_value = value_to_int(value=self.tf_input_value.value, decimal=input_currency.decimal)
            input_value = value_to_int(value=self.tf_output_value.value)
        elif self.dd_input_currency.value == 'ecoin':
            output_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_output_currency.value)
            type_ = RequestTypes.OUTPUT
            output_requisite_data_id = self.dd_output_requisite_data.value
            output_currency_value = value_to_int(value=self.tf_output_value.value, decimal=output_currency.decimal)
            output_value = value_to_int(value=self.tf_input_value.value)
        else:
            input_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_input_currency.value)
            output_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_output_currency.value)
            type_ = RequestTypes.ALL
            input_method_id = self.dd_input_method.value
            input_currency_value = value_to_int(value=self.tf_input_value.value, decimal=input_currency.decimal)
            output_requisite_data_id = self.dd_output_requisite_data.value
            output_currency_value = value_to_int(value=self.tf_output_value.value, decimal=output_currency.decimal)
        try:
            request_id = await self.client.session.api.client.requests.create(
                wallet_id=wallet_id,
                type_=type_,
                input_method_id=input_method_id,
                input_currency_value=input_currency_value,
                input_value=input_value,
                output_requisite_data_id=output_requisite_data_id,
                output_currency_value=output_currency_value,
                output_value=output_value,
            )
            await self.set_type(loading=False)
            await self.client.change_view(
                view=RequestView(request_id=request_id),
                delete_current=True,
                with_restart=True,
            )
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
