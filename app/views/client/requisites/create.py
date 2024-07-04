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

from flet_core import ScrollMode, Row, Column, Container, AlertDialog, alignment, KeyboardType, Image, IconButton, \
    icons, MainAxisAlignment, ExpansionPanel, ExpansionPanelList, colors
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import SubTitle, Text
from app.controls.input import Dropdown, TextField
from app.controls.layout import ClientBaseView
from app.utils import Icons, Fonts, Error, value_to_int
from app.views.client.account.requisite_data.models import RequisiteDataCreateModel
from config import settings
from fexps_api_client.utils import ApiException


class RequisiteTypes:
    INPUT = 'input'
    OUTPUT = 'output'


class RequisiteCreateView(ClientBaseView):
    route = '/client/requisites/create'

    methods = list[dict]
    currencies = list[dict]
    dialog: AlertDialog
    # general
    general_column: Column
    dd_type: Dropdown
    dd_wallet: Dropdown
    dd_currency: Dropdown
    # input
    input_column: Column
    input_subtitle_text: Text
    tf_input_value: TextField
    tf_input_currency_value_min = TextField
    tf_input_currency_value_max = TextField
    dd_input_method: Dropdown
    # common
    common_column: Column
    tf_rate: TextField
    # output
    output_column: Column
    output_subtitle_text: Text
    tf_output_value: TextField
    tf_output_currency_value_min = TextField
    tf_output_currency_value_max = TextField
    dd_output_method: Dropdown
    dd_output_requisite_data: Dropdown
    btn_output_requisite_data: StandardButton

    requisite_data_model: RequisiteDataCreateModel

    async def delete_error_texts(self, _=None) -> None:
        for field in [
            self.dd_type,
            self.dd_wallet,
            self.dd_currency,
            self.tf_input_value,
            self.tf_input_currency_value_min,
            self.tf_input_currency_value_max,
            self.dd_input_method,
            self.tf_rate,
            self.output_subtitle_text,
            self.tf_output_value,
            self.tf_output_currency_value_min,
            self.tf_output_currency_value_max,
            self.dd_output_method,
            self.dd_output_requisite_data,
            self.btn_output_requisite_data,
        ]:
            field.error_text = None
            await field.update_async()

    async def update_subtitle(self, update: bool = True) -> None:
        if not self.dd_type.value or not self.dd_currency.value:
            self.input_subtitle_text.value = await self.client.session.gtv(key='requisite_create_input', currency='')
            self.output_subtitle_text.value = await self.client.session.gtv(key='requisite_create_output', currency='')
            if update:
                await self.input_column.update_async()
                await self.output_column.update_async()
            return
        currency = self.dd_currency.value
        if self.dd_type.value == RequisiteTypes.INPUT:
            self.input_subtitle_text.value = await self.client.session.gtv(
                key='requisite_create_input',
                currency=currency.upper(),
            )
            self.output_subtitle_text.value = await self.client.session.gtv(
                key='requisite_create_output',
                currency=settings.coin_name,
            )
        elif self.dd_type.value == RequisiteTypes.OUTPUT:
            self.input_subtitle_text.value = await self.client.session.gtv(
                key='requisite_create_input',
                currency=settings.coin_name,
            )
            self.output_subtitle_text.value = await self.client.session.gtv(
                key='requisite_create_output',
                currency=currency.upper(),
            )
        if update:
            await self.input_column.update_async()
            await self.output_column.update_async()

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

    async def update_general(self, update: bool = True) -> None:
        type_options = [
            Option(text=await self.client.session.gtv(key=f'requisite_type_{type_}'), key=type_)
            for type_ in [RequisiteTypes.INPUT, RequisiteTypes.OUTPUT]
        ]
        self.dd_type = Dropdown(
            label=await self.client.session.gtv(key='requisite_create_type'),
            on_change=self.change_type_currency,
            options=type_options,
        )
        wallets_options = [
            Option(key=wallet.id, text=f'#{wallet.id} - {wallet.name}')
            for wallet in await self.client.session.api.client.wallets.get_list()
        ]
        self.dd_wallet = Dropdown(
            label=await self.client.session.gtv(key='wallet'),
            options=wallets_options,
            value=wallets_options[0].key,
        )
        currencies_options = [
            Option(text=currency['id_str'].upper(), key=currency['id_str'])
            for currency in self.currencies
        ]
        self.dd_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            on_change=self.change_type_currency,
            options=currencies_options,
        )
        self.general_column = Column(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='requisite_create_general')),
                self.dd_type,
                self.dd_wallet,
                self.dd_currency,
            ],
        )
        if update:
            await self.general_column.update_async()

    async def update_input(self, update: bool = True) -> None:
        self.input_subtitle_text = Text(
            value=None,
            size=24,
            font_family=Fonts.BOLD,
            color=colors.ON_BACKGROUND,
        )
        self.tf_input_value = TextField(
            label=await self.client.session.gtv(key='value'),
            keyboard_type=KeyboardType.NUMBER,
            on_change=self.calculation,
        )
        self.tf_input_currency_value_min = TextField(
            label=await self.client.session.gtv(key='value_min'),
            keyboard_type=KeyboardType.NUMBER,
            disabled=True,
            expand=1,
        )
        self.tf_input_currency_value_max = TextField(
            label=await self.client.session.gtv(key='value_max'),
            keyboard_type=KeyboardType.NUMBER,
            disabled=True,
            expand=1,
        )
        self.dd_input_method = Dropdown(
            label=await self.client.session.gtv(key='requisite_create_input_method'),
            disabled=True,
        )
        self.input_column = Column(
            controls=[
                Row(
                    controls=[
                        self.input_subtitle_text,
                    ],
                ),
                self.tf_input_value,
                self.dd_input_method,
                ExpansionPanelList(
                    controls=[
                        ExpansionPanel(
                            header=Container(
                                content=Text(
                                    value=await self.client.session.gtv(key='requisite_create_extra_options'),
                                    size=18,
                                    font_family=Fonts.BOLD,
                                    color=colors.ON_BACKGROUND,
                                ),
                                bgcolor=colors.BACKGROUND,
                            ),
                            content=Container(
                                content=Row(
                                    controls=[
                                        self.tf_input_currency_value_min,
                                        self.tf_input_currency_value_max,
                                    ],
                                    spacing=16,
                                ),
                                bgcolor=colors.BACKGROUND,
                            ),
                            bgcolor=colors.BACKGROUND,
                            expanded=settings.debug,
                        ),
                    ],
                    expand_icon_color=colors.BACKGROUND,
                ),
            ],
        )
        if update:
            await self.input_column.update_async()

    async def update_common(self, update: bool = True) -> None:
        self.tf_rate = TextField(
            label=await self.client.session.gtv(key='rate'),
            keyboard_type=KeyboardType.NUMBER,
            on_change=self.calculation,
        )
        self.common_column = Column(
            controls=[
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='rate'),
                            size=24,
                            font_family=Fonts.BOLD,
                            color=colors.ON_BACKGROUND,
                        ),
                    ],
                ),
                self.tf_rate,
            ],
        )
        if update:
            await self.common_column.update_async()

    async def update_output(self, update: bool = True) -> None:
        self.output_subtitle_text = Text(
            value=None,
            size=24,
            font_family=Fonts.BOLD,
            color=colors.ON_BACKGROUND,
        )
        self.tf_output_value = TextField(
            label=await self.client.session.gtv(key='value'),
            keyboard_type=KeyboardType.NUMBER,
            on_change=self.calculation,
        )
        self.tf_output_currency_value_min = TextField(
            label=await self.client.session.gtv(key='value_min'),
            keyboard_type=KeyboardType.NUMBER,
            disabled=True,
            expand=1,
        )
        self.tf_output_currency_value_max = TextField(
            label=await self.client.session.gtv(key='value_max'),
            keyboard_type=KeyboardType.NUMBER,
            disabled=True,
            expand=1,
        )
        self.dd_output_method = Dropdown(
            label=await self.client.session.gtv(key='requisite_create_output_method'),
            on_change=self.change_output_method,
            disabled=True,
        )
        self.dd_output_requisite_data = Dropdown(
            label=await self.client.session.gtv(key='requisite_create_output_requisite_data'),
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
                Row(
                    controls=[
                        self.output_subtitle_text,
                    ],
                ),
                self.tf_output_value,
                self.dd_output_method,
                Row(
                    controls=[
                        self.dd_output_requisite_data,
                        self.btn_output_requisite_data,
                    ],
                ),
                ExpansionPanelList(
                    controls=[
                        ExpansionPanel(
                            header=Container(
                                content=Text(
                                    value=await self.client.session.gtv(key='requisite_create_extra_options'),
                                    size=18,
                                    font_family=Fonts.BOLD,
                                    color=colors.ON_BACKGROUND,
                                ),
                                bgcolor=colors.BACKGROUND,
                            ),
                            content=Container(
                                content=Row(
                                    controls=[
                                        self.tf_output_currency_value_min,
                                        self.tf_output_currency_value_max,
                                    ],
                                    spacing=16,
                                ),
                                bgcolor=colors.BACKGROUND,
                            ),
                            bgcolor=colors.BACKGROUND,
                            expanded=settings.debug,
                        ),
                    ],
                    expand_icon_color=colors.BACKGROUND,
                ),
            ],
        )
        if update:
            await self.output_column.update_async()

    async def construct(self):
        self.dialog = AlertDialog(modal=True)
        await self.set_type(loading=True)
        self.methods = await self.client.session.api.client.methods.get_list()
        self.currencies = await self.client.session.api.client.currencies.get_list()
        await self.set_type(loading=False)
        await self.update_general(update=False)
        await self.update_input(update=False)
        await self.update_common(update=False)
        await self.update_output(update=False)
        await self.update_subtitle(update=False)
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='requisite_create_title'),
            with_expand=True,
            main_section_controls=[
                self.dialog,
                Container(
                    content=Column(
                        controls=[
                            self.general_column,
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
                                text=await self.client.session.gtv(key='requisite_create_title'),
                                on_click=self.requisite_create,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
            ],
        )

    async def change_type_currency(self, _=None):
        await self.update_subtitle()
        self.dd_input_method.disabled = True
        self.dd_output_method.disabled = True
        self.dd_output_requisite_data.disabled = True
        if not self.dd_type.value or not self.dd_currency.value:
            self.dd_input_method.value = None
            self.dd_output_method.value = None
            self.dd_output_requisite_data.value = None
            await self.update_async()
            return
        currency = self.dd_currency.value
        if self.dd_type.value == RequisiteTypes.INPUT:
            self.tf_input_currency_value_min.disabled = False
            self.tf_input_currency_value_max.disabled = False
            self.dd_input_method.change_options(options=await self.get_method_options(currency_id_str=currency))
            self.dd_input_method.disabled = False
            self.tf_output_currency_value_min.value, self.tf_output_currency_value_min.disabled = None, True
            self.tf_output_currency_value_max.value, self.tf_output_currency_value_max.disabled = None, True
            self.dd_output_method.value = None
            self.dd_output_requisite_data.value = None
            self.btn_output_requisite_data.disabled = True
        elif self.dd_type.value == RequisiteTypes.OUTPUT:
            self.tf_output_currency_value_min.disabled = False
            self.tf_output_currency_value_max.disabled = False
            output_method_options = await self.get_method_options(currency_id_str=currency)
            self.dd_output_method.change_options(options=output_method_options)
            self.dd_output_method.disabled = False
            self.btn_output_requisite_data.disabled = False
            if not output_method_options:
                self.btn_output_requisite_data.disabled = True
            self.dd_output_requisite_data.value = None
            self.dd_input_method.value = None
            self.tf_input_currency_value_min.value, self.tf_input_currency_value_min.disabled = None, True
            self.tf_input_currency_value_max.value, self.tf_input_currency_value_max.disabled = None, True
            await self.change_output_method()
        await self.calculation()
        await self.update_async()

    async def change_output_method(self, _=None):
        if not self.dd_output_method or not self.dd_output_method.value:
            return
        await self.set_type(loading=True)
        requisites_datas = await self.client.session.api.client.requisites_datas.get_list()
        await self.set_type(loading=False)
        options = []
        for requisite_data in requisites_datas:
            if int(requisite_data.method.id) != int(self.dd_output_method.value):
                continue
            options += [
                Option(text=f'{requisite_data.name}', key=requisite_data.id),
            ]
        self.dd_output_requisite_data.disabled = False
        self.dd_output_requisite_data.change_options(options=options)
        await self.dd_output_requisite_data.update_async()

    async def calculation(self, _=None):
        await self.delete_error_texts()
        if not self.dd_type.value:
            return
        elements = [not self.tf_input_value.value, not self.tf_rate.value, not self.tf_output_value.value]
        input_value_bool = bool(self.tf_input_value.value) and not self.tf_input_value.disabled
        input_value = str(self.tf_input_value.value).replace(',', '.')
        rate_bool = bool(self.tf_rate.value) and not self.tf_rate.disabled
        rate = str(self.tf_rate.value).replace(',', '.')
        output_value_bool = bool(self.tf_output_value.value) and not self.tf_output_value.disabled
        output_value = str(self.tf_output_value.value).replace(',', '.')
        if self.tf_input_value.disabled and (not rate_bool or not output_value_bool):
            self.tf_input_value.value = None
            self.tf_input_value.disabled = False
            await self.tf_input_value.update_async()
        if self.tf_rate.disabled and (not input_value_bool or not output_value_bool):
            self.tf_rate.value = None
            self.tf_rate.disabled = False
            await self.tf_rate.update_async()
        if self.tf_output_value.disabled and (not input_value_bool or not rate_bool):
            self.tf_output_value.value = None
            self.tf_output_value.disabled = False
            await self.tf_output_value.update_async()
        if elements.count(True) > 1:
            return
        for field in [self.tf_input_value, self.tf_rate, self.tf_output_value]:
            if not field.value:
                continue
            if not await Error.check_field(self, field, check_float=True):
                return
        if input_value_bool and rate_bool:
            if self.dd_type.value == RequisiteTypes.INPUT:
                if float(rate) == 0:
                    return
                self.tf_output_value.value = round(float(input_value) / float(rate), 2)
            elif self.dd_type.value == RequisiteTypes.OUTPUT:
                self.tf_output_value.value = round(float(input_value) * float(rate), 2)
            self.tf_output_value.disabled = True
            await self.tf_output_value.update_async()
        elif rate_bool and output_value_bool:
            if self.dd_type.value == RequisiteTypes.INPUT:
                self.tf_input_value.value = round(float(output_value) * float(rate), 2)
            elif self.dd_type.value == RequisiteTypes.OUTPUT:
                if float(rate) == 0:
                    return
                self.tf_input_value.value = round(float(output_value) / float(rate), 2)
            self.tf_input_value.disabled = True
            await self.tf_input_value.update_async()
        elif input_value_bool and output_value_bool:
            if self.dd_type.value == RequisiteTypes.INPUT:
                if float(output_value) == 0:
                    return
                self.tf_rate.value = round(float(input_value) / float(output_value), 2)
            elif self.dd_type.value == RequisiteTypes.OUTPUT:
                if float(input_value) == 0:
                    return
                self.tf_rate.value = round(float(output_value) / float(input_value), 2)
            self.tf_rate.disabled = True
            await self.tf_rate.update_async()

    async def create_output_requisite_data(self, _=None):
        self.requisite_data_model = RequisiteDataCreateModel(
            session=self.client.session,
            update_async=self.update_async,
            after_close=self.create_output_requisite_data_after_close,
            currency_id_str=self.dd_currency.value,
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
        await self.update_async()

    async def create_output_requisite_data_after_close(self):
        self.dialog.open = False
        await self.dialog.update_async()
        await asyncio.sleep(0.1)
        await self.change_output_method()
        if self.dd_currency.value == self.requisite_data_model.currency_id_str:
            if str(self.dd_output_method.value) == str(self.requisite_data_model.method_id):
                self.dd_output_requisite_data.value = self.requisite_data_model.requisite_data_id
        await self.update_async()

    async def create_output_requisite_data_close(self, _=None):
        self.dialog.open = False
        await self.dialog.update_async()

    async def requisite_create(self, _=None):
        await self.set_type(loading=True)
        # check exist
        for _field in [self.dd_type, self.dd_currency]:
            if _field.value is not None:
                continue
            await self.set_type(loading=False)
            _field.error_text = await self.client.session.gtv(key='error_empty')
            await self.update_async()
            return
        # check float
        for _field in [self.tf_input_value, self.tf_output_value]:
            if not await Error.check_field(self, _field, check_float=True):
                await self.set_type(loading=False)
                return
        # check float or None
        for _field in [
            self.tf_input_currency_value_min,
            self.tf_input_currency_value_max,
            self.tf_output_currency_value_min,
            self.tf_output_currency_value_max,
        ]:
            if not _field.value:
                continue
            if not await Error.check_field(self, _field, check_float=True):
                await self.set_type(loading=False)
                return
        type_ = self.dd_type.value
        wallet_id = self.dd_wallet.value
        currency = await self.client.session.api.client.currencies.get(id_str=self.dd_currency.value)
        input_value, rate_value, output_value = None, None, None
        if self.tf_input_value.value and not self.tf_input_value.disabled:
            input_value = self.tf_input_value.value
        if self.tf_rate.value and not self.tf_rate.disabled:
            rate_value = self.tf_rate.value
        if self.tf_output_value.value and not self.tf_output_value.disabled:
            output_value = self.tf_output_value.value
        input_method_id, output_requisite_data_id = None, None
        currency_value, rate, value = None, None, None
        currency_value_min, currency_value_max = None, None
        final_check_list = []
        if type_ == RequisiteTypes.INPUT:
            for _field in [self.dd_input_method]:
                if _field.value is not None:
                    continue
                await self.set_type(loading=False)
                _field.error_text = await self.client.session.gtv(key='error_empty')
                await self.update_async()
                return
            currency_value = value_to_int(value=input_value, decimal=currency.decimal)
            rate = value_to_int(value=rate_value, decimal=currency.rate_decimal)
            value = value_to_int(value=output_value)
            input_method_id = self.dd_input_method.value
            if self.tf_input_currency_value_min.value:
                currency_value_min = value_to_int(
                    value=self.tf_input_currency_value_min.value,
                    decimal=currency.decimal,
                )
            if self.tf_input_currency_value_max.value:
                currency_value_max = value_to_int(
                    value=self.tf_input_currency_value_max.value,
                    decimal=currency.decimal,
                )
            final_check_list = [
                (currency_value, self.tf_input_value, currency),
                (value, self.tf_output_value, None),
                (currency_value_min, self.tf_input_currency_value_min, currency),
                (currency_value_max, self.tf_input_currency_value_max, currency),
            ]
        elif type_ == RequisiteTypes.OUTPUT:
            for _field in [self.dd_output_method, self.dd_output_requisite_data]:
                if _field.value is not None:
                    continue
                await self.set_type(loading=False)
                _field.error_text = await self.client.session.gtv(key='error_empty')
                await self.update_async()
                return
            currency_value = value_to_int(value=output_value, decimal=currency.decimal)
            rate = value_to_int(value=rate_value, decimal=currency.rate_decimal)
            value = value_to_int(value=input_value)
            output_requisite_data_id = self.dd_output_requisite_data.value
            if self.tf_output_currency_value_min.value:
                currency_value_min = value_to_int(
                    value=self.tf_output_currency_value_min.value,
                    decimal=currency.decimal,
                )
            if self.tf_output_currency_value_max.value:
                currency_value_max = value_to_int(
                    value=self.tf_output_currency_value_max.value,
                    decimal=currency.decimal,
                )
            final_check_list = [
                (currency_value, self.tf_output_value, currency),
                (value, self.tf_input_value, None),
                (currency_value_min, self.tf_output_currency_value_min, currency),
                (currency_value_max, self.tf_output_currency_value_max, currency),
            ]
        error_less_div_str = await self.client.session.gtv(key='error_less_div')
        error_div_str = await self.client.session.gtv(key='error_div')
        for _value, _field, _currency in final_check_list:
            if _value is None:
                continue
            div, decimal = settings.default_div, settings.default_decimal
            if _currency:
                div, decimal = _currency['div'], _currency['decimal']
                if int(_value) % div != 0:
                    _field.error_text = f'{error_div_str} {div / (10 ** decimal)}'
                    await self.set_type(loading=False)
                    await self.update_async()
                    return
            if int(_value) < div:
                _field.error_text = f'{error_less_div_str} {div / (10 ** decimal)}'
                await self.set_type(loading=False)
                await self.update_async()
                return
        try:
            await self.client.session.api.client.requisites.create(
                type_=type_,
                wallet_id=wallet_id,
                input_method_id=input_method_id,
                output_requisite_data_id=output_requisite_data_id,
                currency_value=currency_value,
                rate=rate,
                value=value,
                currency_value_min=currency_value_min,
                currency_value_max=currency_value_max,
            )
            await self.set_type(loading=False)
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
