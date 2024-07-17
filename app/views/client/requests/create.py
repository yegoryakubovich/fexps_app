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
from typing import Optional

from flet_core import Column, Container, Row, alignment, Image, colors, ScrollMode, MainAxisAlignment, \
    Divider
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import SubTitle, Text
from app.controls.input import TextField, Dropdown
from app.controls.layout import ClientBaseView
from app.utils import Icons, Fonts, Error, value_to_float, value_to_str
from app.utils.calculations.requests.rate import calculate_request_rate_all_by_input_currency_value, \
    calculate_request_rate_all_by_output_currency_value, calculate_request_rate_input_by_input_currency_value, \
    calculate_request_rate_input_by_input_value, calculate_request_rate_output_by_output_value, \
    calculate_request_rate_output_by_output_currency_value
from app.utils.value import value_to_int
from app.views.client.account.requisite_data.models import RequisiteDataCreateModel
from app.views.client.requests.get import RequestView
from config import settings
from fexps_api_client.utils import ApiException


def copy_options(options: list[Option]) -> list[Option]:
    return [
        Option(key=option.key, text=option.text)
        for option in options
    ]


class RequisiteDataCreateTypes:
    DEFAULT = 'create_default'
    DISPOSABLE = 'create_disposable'


class RequestCreateView(ClientBaseView):
    route = '/client/request/create'

    methods = dict
    currencies = list[dict]
    calculate = dict

    # input
    input_column: Column
    tf_input_value: TextField
    t_input_available_sum: Text
    dd_input_currency: Dropdown
    dd_input_method: Dropdown
    # common
    common_column: Column
    # output
    output_column: Column
    tf_output_value: TextField
    t_output_available_sum: Text
    dd_output_currency: Dropdown
    dd_output_method: Dropdown
    dd_output_requisite_data: Dropdown
    output_requisite_data_column: Column

    tf_account_client_text: TextField

    requisite_data_model: Optional[RequisiteDataCreateModel]

    async def delete_error_texts(self, _=None) -> None:
        fields = [
            self.tf_input_value,
            self.dd_input_currency,
            self.dd_input_method,
            self.tf_output_value,
            self.dd_output_currency,
            self.dd_output_method,
            self.dd_output_requisite_data,
        ]
        for field in fields:
            field.error_text = None
            await field.update_async()

    async def get_currency_options(self, exclude_currency_id_str: str = None) -> list[Option]:
        options = []
        for currency in self.currencies:
            if currency['id_str'] == exclude_currency_id_str:
                continue
            options.append(Option(text=currency['id_str'].upper(), key=currency['id_str']))
        return options

    async def get_method_options(self, currency_id_str: str) -> list[Option]:
        options = []
        for method in self.methods:
            if method.currency.id_str.lower() != currency_id_str.lower():
                continue
            method_str = await self.client.session.gtv(key=method.name_text)
            if self.client.session.debug:
                method_str = f'{method_str} ({method.id})'
            options += [
                Option(text=method_str, key=method.id),
            ]
        return options

    async def get_requisite_data_options(self, method_id: int) -> list[Option]:
        requisites_datas = await self.client.session.api.client.requisites_datas.get_list()
        options = [
            Option(text=await self.client.session.gtv(key=f'request_create_requisite_data_{key}'), key=key)
            for key in [RequisiteDataCreateTypes.DEFAULT, RequisiteDataCreateTypes.DISPOSABLE]
        ]
        for requisite_data in requisites_datas:
            if int(requisite_data.method.id) != method_id:
                continue
            if not requisite_data.allow:
                continue
            options.append(
                Option(text=f'{requisite_data.name}', key=requisite_data.id),
            )
        return options

    """
    SEND
    """

    async def update_input(self, update: bool = True) -> None:
        self.tf_input_value = TextField(
            label=await self.client.session.gtv(key='value'),
            on_change=self.change_value,
            expand=4,
        )
        self.dd_input_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            value=await self.client.session.get_cs(key='request_create_input_currency'),
            options=await self.get_currency_options(),
            on_change=partial(self.change_currency, 'input'),
            expand=2,
        )
        self.t_input_available_sum = Text(value=value_to_str(value=0), font_family=Fonts.BOLD)
        self.dd_input_method = Dropdown(
            label=await self.client.session.gtv(key='request_create_input_method'),
            value=await self.client.session.get_cs(key='request_create_input_method'),
            on_change=self.change_method,
            disabled=True,
        )
        self.input_column = Column(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='request_create_input')),
                Row(
                    controls=[
                        self.tf_input_value,
                        self.dd_input_currency,
                    ],
                    spacing=10,
                ),
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='request_create_available_sum'),
                        ),
                        self.t_input_available_sum,
                    ],
                    spacing=10
                ),
                self.dd_input_method,
            ],
        )
        if update:
            await self.input_column.update_async()

    """
    COMMON
    """

    async def update_common(self, update: bool = True) -> None:
        self.common_column = Column(
            controls=[
                Row(
                    controls=[
                        StandardButton(
                            content=Image(
                                src=Icons.REVERSE,
                                height=18,
                                color=colors.ON_PRIMARY,
                            ),
                            horizontal=5,
                            vertical=5,
                            bgcolor=colors.PRIMARY,
                            on_click=self.reverse_all,
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
        )
        if update:
            await self.common_column.update_async()

    """
    RECEIVE
    """

    async def update_output(self, update: bool = True) -> None:
        self.tf_output_value = TextField(
            label=await self.client.session.gtv(key='value'),
            on_change=self.change_value,
            expand=4,
        )
        self.t_output_available_sum = Text(value=value_to_str(value=0), font_family=Fonts.BOLD)
        self.dd_output_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            options=await self.get_currency_options(),
            value=await self.client.session.get_cs(key='request_create_output_currency'),
            on_change=partial(self.change_currency, 'output'),
            expand=2,
        )
        self.dd_output_method = Dropdown(
            label=await self.client.session.gtv(key='request_create_output_method'),
            value=await self.client.session.get_cs(key='request_create_output_method'),
            on_change=self.change_output_method,
            disabled=True,
        )
        self.dd_output_requisite_data = Dropdown(
            label=await self.client.session.gtv(key='request_create_output_requisite_data'),
            on_change=self.change_output_requisite_data,
            disabled=True,
        )
        self.output_requisite_data_column = Column(controls=[])
        self.output_column = Column(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='request_create_output')),
                Row(
                    controls=[
                        self.tf_output_value,
                        self.dd_output_currency,
                    ],
                    spacing=10,
                ),
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='request_create_available_sum'),
                        ),
                        self.t_output_available_sum,
                    ],
                    spacing=10
                ),
                self.dd_output_method,
                self.dd_output_requisite_data,
                self.output_requisite_data_column,
            ],
        )
        if update:
            await self.output_column.update_async()

    """
    ALL
    """

    async def construct(self):
        self.requisite_data_model = None
        await self.set_type(loading=True)
        self.methods = await self.client.session.api.client.methods.get_list()
        self.currencies = await self.client.session.api.client.currencies.get_list()
        self.currencies.insert(
            0,
            {
                'id': 0,
                'id_str': settings.coin_name,
                'decimal': 2,
                'rate_decimal': 2,
                'div': 100,
            },
        )
        self.calculate = None
        await self.set_type(loading=False)
        await self.update_input(update=False)
        await self.update_common(update=False)
        await self.update_output(update=False)
        self.tf_account_client_text = TextField(
            label=await self.client.session.gtv(key='request_get_client_text'),
            multiline=True,
        )
        await self.write_data()
        self.controls = await self.get_controls(
            with_expand=True,
            title=await self.client.session.gtv(key='request_create_title'),
            main_section_controls=[
                Container(
                    content=Column(
                        controls=[
                            self.input_column,
                            self.common_column,
                            self.output_column,
                            Divider(),
                            self.tf_account_client_text,
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
                                    value=await self.client.session.gtv(key='request_create_button'),
                                    size=settings.get_font_size(multiple=1.5),
                                ),
                                on_click=self.request_create,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
            ],
        )

    async def save_data(self, _=None):
        if self.dd_input_currency.value:
            await self.client.session.set_cs(key='request_create_input_currency', value=self.dd_input_currency.value)
        if self.dd_output_currency.value:
            await self.client.session.set_cs(key='request_create_output_currency', value=self.dd_output_currency.value)
        if self.dd_input_method.value:
            await self.client.session.set_cs(key='request_create_input_method', value=self.dd_input_method.value)
        if self.dd_output_method.value:
            await self.client.session.set_cs(key='request_create_output_method', value=self.dd_output_method.value)

    async def write_data(self, _=None):
        input_currency_value = await self.client.session.get_cs(key='request_create_input_currency')
        if input_currency_value:
            self.dd_input_currency.value = input_currency_value
            await self.change_currency(type_='input', update=False)
        output_currency_value = await self.client.session.get_cs(key='request_create_output_currency')
        if output_currency_value:
            self.dd_output_currency.value = output_currency_value
            await self.change_currency(type_='output', update=False)
        input_method_value = await self.client.session.get_cs(key='request_create_input_method')
        if input_method_value:
            self.dd_input_method.value = input_method_value
            await self.change_method(update=False)
        output_method_value = await self.client.session.get_cs(key='request_create_output_method')
        if output_method_value:
            self.dd_output_method.value = output_method_value
            await self.change_method(update=False)

    async def change_currency(self, type_: str, update: bool = True, _=None):
        if update:
            await self.delete_error_texts()
        self.calculate = None
        await self.set_type(loading=True)
        if type_ == 'input' and self.dd_input_currency.value:
            currency = self.dd_input_currency.value
            self.dd_output_currency.change_options(
                options=await self.get_currency_options(exclude_currency_id_str=currency),
            )
            self.dd_input_method.disabled = False
            self.dd_input_method.change_options(
                options=await self.get_method_options(currency_id_str=currency),
            )
            await self.set_type(loading=False)
        if type_ == 'output' and self.dd_output_currency.value:
            currency = self.dd_output_currency.value
            self.dd_input_currency.change_options(
                options=await self.get_currency_options(exclude_currency_id_str=currency),
            )
            self.dd_output_method.disabled = False
            output_method_options = await self.get_method_options(currency_id_str=currency)
            self.dd_output_method.change_options(options=output_method_options)
            self.dd_output_requisite_data.value = None
            await self.set_type(loading=False)
            await self.change_output_method(update=update)
        if update:
            await self.update_async()
        await self.change_client_text(update=update)
        await self.change_method(update=update)
        await self.save_data()

    async def change_client_text(self, update: bool = True, _=None):
        self.tf_account_client_text.value = ''
        if self.dd_input_currency.value == settings.coin_name:
            request_type = 'output'
        elif self.dd_output_currency.value == settings.coin_name:
            request_type = 'input'
        else:
            request_type = 'all'
        request_state = 'create'
        account_client_text = await self.client.session.api.client.accounts.clients_texts.get(
            key=f'request_{request_type}_{request_state}',
        )
        if account_client_text.value:
            self.tf_account_client_text.value = account_client_text.value
        if update:
            await self.tf_account_client_text.update_async()

    async def change_method(self, update: bool = True, _=None):
        if update:
            await self.delete_error_texts()
        self.calculate = None
        await self.save_data()
        if [self.dd_input_currency.value, self.dd_input_currency.value].count(None) == 2:
            return
        input_method_id, output_method_id = None, None
        if self.dd_input_method.value and self.dd_input_method.value != settings.coin_name:
            input_method_id = self.dd_input_method.value
            try:
                input_method = await self.client.session.api.client.methods.get(id_=input_method_id)
                self.t_input_available_sum.value = value_to_str(
                    value=value_to_float(
                        value=input_method['input_requisites_sum'],
                        decimal=input_method['currency']['decimal'],
                    ),
                )
                if update:
                    await self.t_input_available_sum.update_async()
            except:
                pass
        if self.dd_output_method.value and self.dd_output_currency.value != settings.coin_name:
            output_method_id = self.dd_output_method.value
            try:
                output_method = await self.client.session.api.client.methods.get(id_=output_method_id)
                self.t_output_available_sum.value = value_to_str(
                    value=value_to_float(
                        value=output_method['output_requisites_sum'],
                        decimal=output_method['currency']['decimal'],
                    ),
                )
                if update:
                    await self.t_output_available_sum.update_async()
            except:
                pass
        if self.dd_input_currency.value == settings.coin_name:
            request_type = 'output'
            if not output_method_id:
                return
        elif self.dd_output_currency.value == settings.coin_name:
            request_type = 'input'
            if not input_method_id:
                return
        else:
            request_type = 'all'
            if not input_method_id or not output_method_id:
                return
        try:
            self.calculate = await self.client.session.api.client.requests.calculate(
                wallet_id=self.client.session.wallets[0]['id'],
                type_=request_type,
                input_method_id=input_method_id,
                output_method_id=output_method_id,
            )
        except:
            pass
        await self.calculation(update=update)

    """
    OUTPUT METHOD
    """

    async def change_output_method(self, update: bool = True, _=None):
        if update:
            await self.delete_error_texts()
        if not self.dd_output_method or not self.dd_output_method.value:
            return
        options = await self.get_requisite_data_options(method_id=int(self.dd_output_method.value))
        self.dd_output_requisite_data.disabled = False
        self.dd_output_requisite_data.change_options(options=options)
        await self.change_method(update=update)

    """
    OUTPUT REQUISITE DATA
    """

    async def change_output_requisite_data(self, _=None):
        await self.delete_error_texts()
        self.requisite_data_model = None
        self.output_requisite_data_column.controls = []
        if self.dd_output_requisite_data.value == RequisiteDataCreateTypes.DEFAULT:
            self.requisite_data_model = RequisiteDataCreateModel(
                session=self.client.session,
                update_async=self.update_async,
                currency_id_str=self.dd_output_currency.value,
                method_id=self.dd_output_method.value,
            )
        elif self.dd_output_requisite_data.value == RequisiteDataCreateTypes.DISPOSABLE:
            self.requisite_data_model = RequisiteDataCreateModel(
                session=self.client.session,
                update_async=self.update_async,
                currency_id_str=self.dd_output_currency.value,
                method_id=self.dd_output_method.value,
                is_disposable=True,
            )
        if self.requisite_data_model:
            await self.requisite_data_model.construct()
            self.output_requisite_data_column.controls = self.requisite_data_model.controls
        await self.output_requisite_data_column.update_async()

    """
    BLOCK FIELDS
    """

    async def change_value(self, _=None):
        if self.tf_input_value.value and not self.tf_input_value.disabled:
            self.tf_output_value.value = None
            self.tf_output_value.disabled = True
            await self.tf_output_value.update_async()
            if not await Error.check_field(self, field=self.tf_input_value, check_float=True):
                return
        elif self.tf_output_value.value and not self.tf_output_value.disabled:
            self.tf_input_value.value = None
            self.tf_input_value.disabled = True
            await self.tf_input_value.update_async()
            if not await Error.check_field(self, field=self.tf_output_value, check_float=True):
                return
        elif not self.tf_input_value.value and self.tf_output_value.disabled:
            self.tf_input_value.error_text = None
            await self.tf_input_value.update_async()
            self.tf_output_value.value = None
            self.tf_output_value.disabled = False
            await self.tf_output_value.update_async()
        elif not self.tf_output_value.value and self.tf_input_value.disabled:
            self.tf_output_value.error_text = None
            await self.tf_output_value.update_async()
            self.tf_input_value.value = None
            self.tf_input_value.disabled = False
            await self.tf_input_value.update_async()
        await self.calculation()

    """
    REVERSE
    """

    async def reverse_all(self, _=None):
        self.calculate = None
        await self.reverse_currency()
        await self.reverse_method()
        await self.reverse_value()

    async def reverse_currency(self):
        new_input_currency = (copy_options(self.dd_output_currency.options), self.dd_output_currency.value)
        new_output_currency = (copy_options(self.dd_input_currency.options), self.dd_input_currency.value)
        self.dd_input_currency.change_options(options=new_input_currency[0])
        self.dd_input_currency.value = new_input_currency[1]
        await self.dd_input_currency.update_async()
        self.dd_output_currency.change_options(options=new_output_currency[0])
        self.dd_output_currency.value = new_output_currency[1]
        await self.dd_output_currency.update_async()

    async def reverse_method(self):
        new_input_method = (copy_options(self.dd_output_method.options), self.dd_output_method.value)
        new_output_method = (copy_options(self.dd_input_method.options), self.dd_input_method.value)
        self.dd_input_method.change_options(options=new_input_method[0])
        self.dd_input_method.value = new_input_method[1]
        await self.dd_input_method.update_async()
        await self.change_method()
        self.dd_output_method.change_options(options=new_output_method[0])
        self.dd_output_method.value = new_output_method[1]
        await self.dd_output_method.update_async()
        self.dd_output_requisite_data.value = None
        await self.dd_output_requisite_data.update_async()
        await self.change_output_method()

    async def reverse_value(self):
        if self.tf_input_value.value and not self.tf_input_value.disabled:
            new_value = self.tf_input_value.value
            self.tf_input_value.value = None
            self.tf_input_value.disabled = False
            await self.tf_input_value.update_async()
            self.tf_output_value.value = new_value
            self.tf_output_value.disabled = False
            await self.tf_output_value.update_async()
        elif self.tf_output_value.value and not self.tf_output_value.disabled:
            new_value = self.tf_output_value.value
            self.tf_output_value.value = None
            self.tf_output_value.disabled = False
            await self.tf_output_value.update_async()
            self.tf_input_value.value = new_value
            self.tf_input_value.disabled = False
            await self.tf_input_value.update_async()
        await self.calculation()

    """
    CALCULATION | CREATE
    """

    async def calculation(self, update: bool = True, _=None):
        if update:
            await self.delete_error_texts()
        if not self.calculate:
            return
        if self.tf_input_value.value and not self.tf_input_value.disabled:
            if self.dd_output_currency.value == settings.coin_name:
                input_currency = self.calculate['input_method']['currency']
                _input_currency_value = value_to_int(
                    value=self.tf_input_value.value,
                    decimal=input_currency['decimal'],
                )
                result_value = await calculate_request_rate_input_by_input_currency_value(
                    calculation=self.calculate,
                    input_currency_value=_input_currency_value,
                )
                if not result_value:
                    return
                self.tf_output_value.value = result_value
            elif self.dd_input_currency.value == settings.coin_name:
                output_currency = self.calculate['output_method']['currency']
                _output_value = value_to_int(
                    value=self.tf_input_value.value,
                    decimal=output_currency['decimal'],
                )
                result_value = await calculate_request_rate_output_by_output_value(
                    calculation=self.calculate,
                    output_value=_output_value,
                )
                if not result_value:
                    return
                self.tf_output_value.value = result_value
            else:
                input_currency = self.calculate['input_method']['currency']
                _input_currency_value = value_to_int(
                    value=self.tf_input_value.value,
                    decimal=input_currency['decimal'],
                )
                result_value = await calculate_request_rate_all_by_input_currency_value(
                    calculation=self.calculate,
                    input_currency_value=_input_currency_value,
                )
                if not result_value:
                    return
                self.tf_output_value.value = result_value
            self.tf_output_value.disabled = True
            if update:
                await self.tf_output_value.update_async()
        elif self.tf_output_value.value and not self.tf_output_value.disabled:
            if self.dd_output_currency.value == settings.coin_name:
                input_currency = self.calculate['input_method']['currency']
                _input_value = value_to_int(
                    value=self.tf_output_value.value,
                    decimal=input_currency['decimal'],
                )
                result_value = await calculate_request_rate_input_by_input_value(
                    calculation=self.calculate,
                    input_value=_input_value,
                )
            elif self.dd_input_currency.value == settings.coin_name:
                output_currency = self.calculate['output_method']['currency']
                _output_currency_value = value_to_int(
                    value=self.tf_output_value.value,
                    decimal=output_currency['decimal'],
                )
                result_value = await calculate_request_rate_output_by_output_currency_value(
                    calculation=self.calculate,
                    output_currency_value=_output_currency_value,
                )
            else:
                input_currency = self.calculate['input_method']['currency']
                _output_currency_value = value_to_int(
                    value=self.tf_output_value.value,
                    decimal=input_currency['decimal'],
                )
                result_value = await calculate_request_rate_all_by_output_currency_value(
                    calculation=self.calculate,
                    output_currency_value=_output_currency_value,
                )
            self.tf_input_value.value = result_value if result_value else None
            self.tf_input_value.disabled = True
            if update:
                await self.tf_input_value.update_async()

    async def request_create(self, _=None):
        if len(self.client.session.wallets) == 1:
            return await self.go_request_create(wallet_id=self.client.session.wallets[0]['id'])
        # FIXME (1+ wallets)
        return await self.go_request_create(wallet_id=self.client.session.wallets[0]['id'])

    async def go_request_create(self, wallet_id: int):
        if self.requisite_data_model:
            if not await self.requisite_data_model.create_requisite_data():
                return
            if self.dd_output_currency.value == self.requisite_data_model.currency_id_str:
                if str(self.dd_output_method.value) == str(self.requisite_data_model.method_id):
                    self.dd_output_requisite_data.value = self.requisite_data_model.requisite_data_id
        await self.set_type(loading=True)
        for field in [self.dd_input_currency, self.dd_output_currency]:
            if field.value is not None:
                continue
            await self.set_type(loading=False)
            await Error.field_error_set(
                fields=[field],
                text=await self.client.session.gtv(key='error_empty'),
            )
            return
        input_currency, output_currency = None, None
        input_method_id, output_requisite_data_id = None, None
        if self.dd_output_currency.value == settings.coin_name:
            request_type = 'input'
            input_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_input_currency.value)
            if self.dd_input_method.value is None:
                await self.set_type(loading=False)
                await Error.field_error_set(
                    fields=[self.dd_input_method],
                    text=await self.client.session.gtv(key='error_empty'),
                )
                return
            input_method_id = self.dd_input_method.value
        elif self.dd_input_currency.value == settings.coin_name:
            request_type = 'output'
            output_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_output_currency.value)
            if self.dd_output_requisite_data.value is None:
                await self.set_type(loading=False)
                await Error.field_error_set(
                    fields=[self.dd_output_requisite_data],
                    text=await self.client.session.gtv(key='error_empty'),
                )
                return
            output_requisite_data_id = self.dd_output_requisite_data.value
        else:
            request_type = 'all'
            input_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_input_currency.value)
            output_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_output_currency.value)
            if self.dd_input_method.value is None:
                await self.set_type(loading=False)
                await Error.field_error_set(
                    fields=[self.dd_input_method],
                    text=await self.client.session.gtv(key='error_empty'),
                )
                return
            input_method_id = self.dd_input_method.value
            if self.dd_output_requisite_data.value is None:
                await self.set_type(loading=False)
                await Error.field_error_set(
                    fields=[self.dd_output_requisite_data],
                    text=await self.client.session.gtv(key='error_empty'),
                )
                return
            output_requisite_data_id = self.dd_output_requisite_data.value
        input_value, output_value = None, None
        error_less_div_str = await self.client.session.gtv(key='error_less_div')
        error_div_str = await self.client.session.gtv(key='error_div')
        for field, field_currency in [
            (self.tf_input_value, input_currency),
            (self.tf_output_value, output_currency),
        ]:
            if field.value and not field.disabled:
                if not await Error.check_field(self, field, check_float=True):
                    await self.set_type(loading=False)
                    return
                decimal = settings.default_decimal
                div_float = settings.default_div / (10 ** decimal)
                field_float = float(field.value)
                if field_currency:
                    decimal = field_currency['decimal']
                    div_float = field_currency['div'] / (10 ** decimal)
                    if field_float % div_float != 0:
                        await self.set_type(loading=False)
                        await Error.field_error_set(
                            fields=[field],
                            text=f'{error_div_str} ({div_float})',
                        )
                        return
                if field_float < div_float:
                    await self.set_type(loading=False)
                    await Error.field_error_set(
                        fields=[field],
                        text=f'{error_less_div_str} {div_float}',
                    )
                    return
        if self.tf_input_value.value and not self.tf_input_value.disabled:
            input_value = value_to_int(
                value=self.tf_input_value.value,
                decimal=input_currency['decimal'] if input_currency else settings.default_decimal,
            )
        if self.tf_output_value.value and not self.tf_output_value.disabled:
            output_value = value_to_int(
                value=self.tf_output_value.value,
                decimal=output_currency['decimal'] if output_currency else settings.default_decimal,
            )
        if [input_value, output_value].count(None) > 1:
            await self.set_type(loading=False)
            await Error.field_error_set(
                fields=[self.tf_input_value, self.tf_output_value],
                text=await self.client.session.gtv(key='error_one_value_required'),
            )
            return
        try:
            request_id = await self.client.session.api.client.requests.create(
                name=None,
                wallet_id=wallet_id,
                type_=request_type,
                input_method_id=input_method_id,
                output_requisite_data_id=output_requisite_data_id,
                input_value=input_value,
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
