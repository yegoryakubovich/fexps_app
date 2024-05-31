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

from flet_core import Column, Container, KeyboardType, Row, alignment, Control, AlertDialog, Image, colors, ScrollMode, \
    IconButton, icons, MainAxisAlignment
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import SubTitle, Text
from app.controls.input import TextField, Dropdown
from app.controls.layout import ClientBaseView
from app.utils import Icons, Fonts, value_to_float, Error
from app.utils.value import value_to_int
from app.views.client.account.requisite_data.models import RequisiteDataCreateModel
from app.views.client.requests.get import RequestView
from config import settings
from fexps_api_client.utils import ApiException


class RequestTypes:
    INPUT = 'input'
    OUTPUT = 'output'
    ALL = 'all'


class RequestCreateView(ClientBaseView):
    route = '/client/request/create'

    methods = dict
    currencies = list[dict]
    dialog: AlertDialog

    # input
    tf_input_value = TextField(value=None)
    dd_input_currency = Dropdown(value=None)
    dd_input_method = Dropdown(value=None)

    # output
    tf_output_value = TextField(value=None)
    dd_output_currency = Dropdown(value=None)
    dd_output_method = Dropdown(value=None)
    dd_output_requisite_data = Dropdown(value=None)
    requisite_data_model: RequisiteDataCreateModel

    """
    SEND
    """

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

    async def get_input(self) -> list[Control]:
        self.tf_input_value = TextField(
            label=await self.client.session.gtv(key='value'),
            keyboard_type=KeyboardType.NUMBER,
            on_change=self.maybe_calculate,
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
            disabled=True,
            on_change=self.maybe_calculate,
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
            on_change=self.maybe_calculate,
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
            on_change=self.maybe_calculate,
            disabled=True,
            expand=True,
        )
        return [
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
                    StandardButton(
                        content=Image(
                            src=Icons.CREATE,
                            height=10,
                            color=colors.ON_PRIMARY,
                        ),
                        vertical=7,
                        horizontal=7,
                        bgcolor=colors.PRIMARY,
                        on_click=self.create_output_requisite_data,
                    ),
                ]
            )
        ]

    async def construct(self):
        self.dialog = AlertDialog(modal=True)
        await self.set_type(loading=True)
        self.methods = await self.client.session.api.client.methods.get_list()
        self.currencies = await self.client.session.api.client.currencies.get_list()
        self.currencies.insert(
            0,
            {
                'id': 0,
                'id_str': 'ya_coin',
                'decimal': 2,
                'rate_decimal': 2,
                'div': 100,
            }
        )
        await self.set_type(loading=False)
        self.controls = await self.get_controls(
            with_expand=True,
            title=await self.client.session.gtv(key='request_create_title'),
            main_section_controls=[
                Container(
                    content=Column(
                        controls=[
                            self.dialog,
                            *await self.get_input(),
                            *await self.get_output(),
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

    async def change_currency(self, type_: str, _):
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
        if type_ == 'output' and self.dd_output_currency.value:
            currency = self.dd_output_currency.value
            self.dd_input_currency.change_options(
                options=await self.get_currency_options(exclude_currency_id_str=currency),
            )
            self.dd_output_method.disabled = False
            self.dd_output_method.change_options(
                options=await self.get_method_options(currency_id_str=currency),
            )
            self.dd_output_requisite_data.value = None
        await self.set_type(loading=False)
        await self.update_async()
        await self.maybe_calculate(_)

    """
    OUTPUT
    """

    async def change_output_method(self, _):
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
        await self.maybe_calculate(_)

    async def create_output_requisite_data(self, _):
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
                         ] + self.requisite_data_model.controls,
                scroll=ScrollMode.AUTO,
            ),
            width=400,
        )
        self.dialog.actions = self.requisite_data_model.buttons
        self.dialog.open = True
        await self.dialog.update_async()

    async def create_output_requisite_data_after_close(self):
        self.dialog.open = False
        await self.dialog.update_async()
        await asyncio.sleep(0.1)
        await self.change_output_method('')
        if self.dd_output_currency.value == self.requisite_data_model.currency_id_str:
            if str(self.dd_output_method.value) == str(self.requisite_data_model.method_id):
                self.dd_output_requisite_data.value = self.requisite_data_model.requisite_data_id
        await self.update_async()

    async def create_output_requisite_data_close(self, _):
        self.dialog.open = False
        await self.dialog.update_async()

    async def request_create(self, _):
        if self.tf_input_value.value and self.tf_output_value.value:
            self.tf_output_value.error_text = await self.client.session.gtv(key='request_create_error_only_one_fields')
            await self.update_async()
            return
        if len(self.client.session.wallets) == 1:
            return await self.go_request_create(wallet_id=self.client.session.wallets[0]['id'])
        # FIXME (1+ wallets)

    async def maybe_calculate(self, _):
        if not self.tf_input_value.value and self.tf_output_value.disabled:
            self.tf_output_value.value = None
            self.tf_output_value.disabled = False
            await self.tf_output_value.update_async()
        if not self.tf_output_value.value and self.tf_input_value.disabled:
            self.tf_input_value.value = None
            self.tf_input_value.disabled = False
            await self.tf_input_value.update_async()
        if not self.tf_input_value.value and not self.tf_output_value.value:
            return
        input_method_id, output_requisite_data_id = None, None
        for field in [self.dd_input_currency, self.dd_output_currency]:
            if field.value is None:
                return
        for field in [self.tf_input_value, self.tf_output_value]:
            if not field.value:
                continue
            if not await Error.check_field(self, field, check_float=True):
                field.error_text = await self.client.session.gtv(key='error_not_float')
                await field.update_async()
                return
        if self.dd_output_currency.value == 'ya_coin':
            type_ = RequestTypes.INPUT
            if not self.dd_input_method.value:
                return
            input_method_id = self.dd_input_method.value
        elif self.dd_input_currency.value == 'ya_coin':
            type_ = RequestTypes.OUTPUT
            if not self.dd_output_requisite_data.value:
                return
            output_requisite_data_id = self.dd_output_requisite_data.value
        else:
            type_ = RequestTypes.ALL
            if not self.dd_input_method.value or self.dd_output_requisite_data.value:
                return
            input_method_id = self.dd_input_method.value
            output_requisite_data_id = self.dd_output_requisite_data.value
        try:
            rate_info = await self.client.session.api.client.requests.calc(
                type_=type_,
                input_method_id=input_method_id,
                output_requisite_data_id=output_requisite_data_id,
            )
        except ApiException:
            return
        rate_float: float = value_to_float(value=rate_info.rate, decimal=rate_info.rate_decimal)
        if self.tf_input_value.value and not self.tf_input_value.disabled:
            self.tf_output_value.value = float(self.tf_input_value.value) / rate_float
            self.tf_output_value.disabled = True
            await self.tf_output_value.update_async()
        elif self.tf_output_value.value and not self.tf_output_value.disabled:
            self.tf_input_value.value = float(self.tf_output_value.value) * rate_float
            self.tf_input_value.disabled = True
            await self.tf_input_value.update_async()

    async def go_request_create(self, wallet_id: int):
        input_currency, output_currency = None, None
        input_method_id, input_currency_value, input_value = None, None, None
        output_requisite_data_id, output_currency_value, output_value = None, None, None
        for field in [self.dd_input_currency, self.dd_output_currency]:
            if field.value is not None:
                continue
            field.error_text = await self.client.session.gtv(key='error_empty')
            await self.update_async()
            return
        for field in [self.tf_input_value, self.tf_output_value]:
            if not await Error.check_field(self, field, check_float=True):
                field.error_text = await self.client.session.gtv(key='error_not_float')
                await field.update_async()
                return
        value_list = [value_to_int(value=self.tf_input_value.value), value_to_int(value=self.tf_output_value.value)]
        if value_list.count(None) == 2:
            self.tf_input_value.error_text = await self.client.session.gtv(key='error_empty')
            self.tf_output_value.error_text = await self.client.session.gtv(key='error_empty')
            await self.update_async()
            return
        await self.set_type(loading=True)
        if self.dd_output_currency.value == 'ya_coin':
            input_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_input_currency.value)
            type_ = RequestTypes.INPUT
            if self.dd_input_method.value:
                input_method_id = self.dd_input_method.value
            input_currency_value = value_to_int(value=self.tf_input_value.value, decimal=input_currency.decimal)
            if self.tf_input_value.disabled:
                input_currency_value = None
            input_value = value_to_int(value=self.tf_output_value.value)
            if self.tf_output_value.disabled:
                input_value = None
        elif self.dd_input_currency.value == 'ya_coin':
            output_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_output_currency.value)
            type_ = RequestTypes.OUTPUT
            if self.dd_output_requisite_data.value:
                output_requisite_data_id = self.dd_output_requisite_data.value
            output_currency_value = value_to_int(value=self.tf_output_value.value, decimal=output_currency.decimal)
            if self.tf_output_value.disabled:
                output_currency_value = None
            output_value = value_to_int(value=self.tf_input_value.value)
            if self.tf_input_value.disabled:
                output_value = None
        else:
            input_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_input_currency.value)
            output_currency = await self.client.session.api.client.currencies.get(id_str=self.dd_output_currency.value)
            type_ = RequestTypes.ALL
            if self.dd_input_method.value:
                input_method_id = self.dd_input_method.value
            if self.dd_output_requisite_data.value:
                output_requisite_data_id = self.dd_output_requisite_data.value
            input_currency_value = value_to_int(value=self.tf_input_value.value, decimal=input_currency.decimal)
            if self.tf_input_value.disabled:
                input_currency_value = None
            output_currency_value = value_to_int(value=self.tf_output_value.value, decimal=output_currency.decimal)
            if self.tf_output_value.disabled:
                output_currency_value = None
        error_less_div_str = await self.client.session.gtv(key='error_less_div')
        error_div_str = await self.client.session.gtv(key='error_div')
        for value, field, currency in [
            (input_currency_value, self.tf_input_value, input_currency),
            (input_value, self.tf_output_value, None),
            (output_currency_value, self.tf_output_value, output_currency),
            (output_value, self.tf_input_value, None),
        ]:
            if value is None:
                continue
            div, decimal = settings.default_div, settings.default_decimal
            if currency:
                div, decimal = currency['div'], currency['decimal']
                if int(value) % div != 0:
                    field.error_text = f'{error_div_str} {div / (10 ** decimal)}'
                    await self.set_type(loading=False)
                    await self.update_async()
                    return
            if int(value) < div:
                field.error_text = f'{error_less_div_str} {div / (10 ** decimal)}'
                await self.set_type(loading=False)
                await self.update_async()
                return
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
