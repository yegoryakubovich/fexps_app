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


import asyncio
from functools import partial

from flet_core import Column, Container, Row, alignment, AlertDialog, Image, colors, ScrollMode, IconButton, icons, \
    MainAxisAlignment
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import SubTitle, Text
from app.controls.input import TextField, Dropdown
from app.controls.layout import ClientBaseView
from app.utils import Icons, Fonts, Error
from app.utils.calculations.requests.rate import calculate_request_rate_all_by_input_currency_value, \
    calculate_request_rate_all_by_output_currency_value, calculate_request_rate_input_by_input_currency_value, \
    calculate_request_rate_input_by_input_value, calculate_request_rate_output_by_output_value, \
    calculate_request_rate_output_by_output_currency_value
from app.utils.value import value_to_int
from app.views.client.account.requisite_data.models import RequisiteDataCreateModel
from app.views.client.requests.get import RequestView
from config import settings
from fexps_api_client.utils import ApiException


class RequestTypes:
    INPUT = 'input'
    OUTPUT = 'output'
    ALL = 'all'


def copy_options(options: list[Option]) -> list[Option]:
    return [
        Option(key=option.key, text=option.text)
        for option in options
    ]


class RequestCreateView(ClientBaseView):
    route = '/client/request/create'

    methods = dict
    currencies = list[dict]
    calculate = dict
    dialog: AlertDialog

    # input
    input_column: Column
    tf_input_value: TextField
    dd_input_currency: Dropdown
    dd_input_method: Dropdown
    # common
    common_column: Column
    # output
    output_column: Column
    tf_output_value: TextField
    dd_output_currency: Dropdown
    dd_output_method: Dropdown
    dd_output_requisite_data: Dropdown
    btn_output_requisite_data: StandardButton

    requisite_data_model: RequisiteDataCreateModel

    async def delete_error_texts(self, _=None) -> None:
        fields = [
            self.tf_input_value,
            self.dd_input_currency,
            self.dd_input_method,
            self.tf_output_value,
            self.dd_output_currency,
            self.dd_output_method,
            self.dd_output_requisite_data,
            self.btn_output_requisite_data,
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
            if settings.debug:
                method_str = f'{method_str} ({method.id})'
            options += [
                Option(text=method_str, key=method.id),
            ]
        return options

    """
    SEND
    """

    async def update_input(self, update: bool = True) -> None:
        self.tf_input_value = TextField(
            label=await self.client.session.gtv(key='value'),
            on_change=self.calculation,
            expand=4,
        )
        self.dd_input_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            options=await self.get_currency_options(),
            on_change=partial(self.change_currency, 'input'),
            expand=1,
        )

        self.dd_input_method = Dropdown(
            label=await self.client.session.gtv(key='request_create_input_method'),
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
                    spacing=16,
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
                    spacing=16,
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
            on_change=self.calculation,
            expand=4,
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
            on_change=self.change_output_requisite_data,
            disabled=True,
            expand=True,
        )
        self.btn_output_requisite_data = StandardButton(
            content=Image(
                src=Icons.CREATE,
                height=10,
                color=colors.ON_PRIMARY,
            ),
            vertical=7,
            horizontal=7,
            bgcolor=colors.PRIMARY,
            on_click=self.create_output_requisite_data,
            disabled=True,
        )
        self.output_column = Column(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='request_create_output')),
                Row(
                    controls=[
                        self.tf_output_value,
                        self.dd_output_currency,
                    ],
                    spacing=16,
                ),
                self.dd_output_method,
                Row(
                    controls=[
                        self.dd_output_requisite_data,
                        self.btn_output_requisite_data,
                    ]
                )
            ],
        )
        if update:
            await self.output_column.update_async()

    """
    ALL
    """

    async def construct(self):
        self.dialog = AlertDialog(modal=True)
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
            }
        )
        self.calculate = None
        await self.set_type(loading=False)
        await self.update_input(update=False)
        await self.update_common(update=False)
        await self.update_output(update=False)
        self.controls = await self.get_controls(
            with_expand=True,
            title=await self.client.session.gtv(key='request_create_title'),
            main_section_controls=[
                Container(
                    content=Column(
                        controls=[
                            self.dialog,
                            self.input_column,
                            self.common_column,
                            self.output_column,
                        ],
                        scroll=ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                text=await self.client.session.gtv(key='request_create_button'),
                                on_click=self.request_create,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
            ],
        )

    async def change_currency(self, type_: str, _=None):
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
            self.btn_output_requisite_data.disabled = False
            if not output_method_options:
                self.btn_output_requisite_data.disabled = True
            self.dd_output_requisite_data.value = None
            await self.set_type(loading=False)
            await self.change_output_method()
        await self.update_async()
        await self.change_method()

    async def change_method(self, _=None):
        await self.delete_error_texts()
        self.calculate = None
        if [self.dd_input_currency.value, self.dd_output_currency.value].count(None) == 2:
            return
        input_method_id, output_method_id = None, None
        if self.dd_input_currency.value == settings.coin_name:
            request_type = 'output'
            output_method_id = self.dd_output_method.value
            if not output_method_id:
                return
        elif self.dd_output_currency.value == settings.coin_name:
            request_type = 'input'
            input_method_id = self.dd_input_method.value
            if not input_method_id:
                return
        else:
            request_type = 'all'
            input_method_id = self.dd_input_method.value
            output_method_id = self.dd_output_method.value
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
        await self.calculation()

    """
    OUTPUT
    """

    async def change_output_method(self, _=None):
        await self.delete_error_texts()
        if not self.dd_output_method or not self.dd_output_method.value:
            return
        await self.set_type(loading=True)
        requisites_datas = await self.client.session.api.client.requisites_datas.get_list()
        options = []
        for requisite_data in requisites_datas:
            if int(requisite_data.method.id) != int(self.dd_output_method.value):
                continue
            options.append(
                Option(text=f'{requisite_data.name}', key=requisite_data.id),
            )
        self.dd_output_requisite_data.disabled = False
        self.dd_output_requisite_data.change_options(options=options)
        await self.set_type(loading=False)
        await self.change_method()

    async def change_output_requisite_data(self, _=None):
        await self.delete_error_texts()

    async def create_output_requisite_data(self, _=None):
        await self.delete_error_texts()
        self.requisite_data_model = RequisiteDataCreateModel(
            session=self.client.session,
            update_async=self.update_async,
            after_close=self.create_output_requisite_data_after_close,
            currency_id_str=self.dd_output_currency.value,
            method_id=self.dd_output_method.value,
        )
        await self.requisite_data_model.construct()
        self.dialog.content = Container(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Text(
                                value=self.requisite_data_model.title,
                                size=12,
                                font_family=Fonts.BOLD,
                                color=colors.ON_BACKGROUND,
                            ),
                            IconButton(
                                icon=icons.CLOSE,
                                on_click=self.create_output_requisite_data_close,
                                icon_color=colors.ON_BACKGROUND,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    *self.requisite_data_model.controls,
                ],
                scroll=ScrollMode.AUTO,
            ),
            width=400,
        )
        self.dialog.actions = self.requisite_data_model.buttons
        self.dialog.open = True
        await self.dialog.update_async()
        await self.change_method()

    async def create_output_requisite_data_after_close(self):
        self.dialog.open = False
        await self.dialog.update_async()
        await asyncio.sleep(0.1)
        await self.change_output_method()
        if self.dd_output_currency.value == self.requisite_data_model.currency_id_str:
            if str(self.dd_output_method.value) == str(self.requisite_data_model.method_id):
                self.dd_output_requisite_data.value = self.requisite_data_model.requisite_data_id
        await self.update_async()

    async def create_output_requisite_data_close(self, _=None):
        self.dialog.open = False
        await self.dialog.update_async()

    """
    ALL
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

    async def calculation(self, _=None):
        await self.delete_error_texts()
        if not self.calculate:
            if self.tf_output_value.disabled:
                self.tf_output_value.value = None
                self.tf_output_value.disabled = False
                await self.tf_output_value.update_async()
            if self.tf_input_value.disabled:
                self.tf_input_value.value = None
                self.tf_input_value.disabled = False
                await self.tf_input_value.update_async()
            return
        if not self.tf_input_value.value and self.tf_output_value.disabled:
            self.tf_output_value.value = None
            self.tf_output_value.disabled = False
            await self.tf_output_value.update_async()
        if not self.tf_output_value.value and self.tf_input_value.disabled:
            self.tf_input_value.value = None
            self.tf_input_value.disabled = False
            await self.tf_input_value.update_async()
        if self.tf_input_value.value:
            if not await Error.check_field(self, self.tf_input_value, check_float=True):
                return
        elif self.tf_output_value.value:
            if not await Error.check_field(self, self.tf_output_value, check_float=True):
                return
        # for field in [self.tf_input_value, self.tf_output_value]:
        #     if not field.value:
        #         continue
        #     if not await Error.check_field(self, field, check_float=True):
        #         return
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
            await self.tf_input_value.update_async()

    async def request_create(self, _=None):
        if len(self.client.session.wallets) == 1:
            return await self.go_request_create(wallet_id=self.client.session.wallets[0]['id'])
        # FIXME (1+ wallets)
        return await self.go_request_create(wallet_id=self.client.session.wallets[0]['id'])

    async def go_request_create(self, wallet_id: int):
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
