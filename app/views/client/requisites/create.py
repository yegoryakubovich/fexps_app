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
from typing import Optional

from flet_core import ScrollMode, Row, Column, Container, AlertDialog, alignment, Image, IconButton, icons, \
    MainAxisAlignment, colors, ExpansionTile, border
from flet_core.dropdown import Option

from app.controls.button import StandardButton, SwitchButton
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
    optional_container: Container
    # input
    input_column: Column
    input_subtitle_text: Text
    tf_input_value: TextField
    tf_input_currency_value_min = TextField
    tf_input_currency_value_max = TextField
    dd_input_method: Dropdown
    tf_input_rate: TextField
    btn_input_flex: Optional[SwitchButton]
    # output
    output_column: Column
    output_subtitle_text: Text
    tf_output_value: TextField
    tf_output_currency_value_min = TextField
    tf_output_currency_value_max = TextField
    dd_output_method: Dropdown
    dd_output_requisite_data: Dropdown
    btn_output_requisite_data: StandardButton
    tf_output_rate: TextField

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
            self.tf_input_rate,
            self.output_subtitle_text,
            self.tf_output_value,
            self.tf_output_currency_value_min,
            self.tf_output_currency_value_max,
            self.dd_output_method,
            self.dd_output_requisite_data,
            self.btn_output_requisite_data,
            self.tf_output_rate,
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
            if self.client.session.debug:
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
            size=settings.get_font_size(multiple=2.5),
            font_family=Fonts.BOLD,
            color=colors.ON_BACKGROUND,
        )
        self.tf_input_value = TextField(
            label=await self.client.session.gtv(key='value'),
        )
        self.dd_input_method = Dropdown(
            label=await self.client.session.gtv(key='requisite_create_input_method'),
        )
        self.tf_input_currency_value_min = TextField(
            label=await self.client.session.gtv(key='value_min'),
            expand=1,
        )
        self.tf_input_currency_value_max = TextField(
            label=await self.client.session.gtv(key='value_max'),
            expand=1,
        )
        self.tf_input_rate = TextField(
            label=await self.client.session.gtv(key='rate'),
            expand=True,
        )
        self.btn_input_flex = SwitchButton(
            label=await self.client.session.gtv(key='requisite_create_flex'),
            on_change=self.change_input_flex_btn,
            value=False,
            disabled='requisite_flex' not in self.client.session.account.permissions,
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
                Container(
                    content=ExpansionTile(
                        title=Text(
                            value=await self.client.session.gtv(key='requisite_create_extra_options'),
                            size=settings.get_font_size(multiple=2),
                            font_family=Fonts.BOLD,
                            color=colors.ON_BACKGROUND,
                        ),
                        maintain_state=True,
                        controls=[
                            Row(
                                controls=[
                                    self.tf_input_currency_value_min,
                                    self.tf_input_currency_value_max,
                                ],
                                spacing=10,
                            ),
                        ],
                        bgcolor=colors.BACKGROUND,
                        collapsed_bgcolor=colors.BACKGROUND,
                        icon_color=colors.ON_BACKGROUND,
                        collapsed_icon_color=colors.ON_BACKGROUND,
                        initially_expanded=self.client.session.debug,
                    ),
                    border=border.all(color=colors.ON_BACKGROUND, width=1),
                ),
                Row(
                    controls=[
                        self.tf_input_rate,
                        self.btn_input_flex,
                    ]
                ),
            ],
        )
        if update:
            await self.input_column.update_async()

    async def update_output(self, update: bool = True) -> None:
        self.output_subtitle_text = Text(
            value=None,
            size=settings.get_font_size(multiple=2.5),
            font_family=Fonts.BOLD,
            color=colors.ON_BACKGROUND,
        )
        self.tf_output_value = TextField(
            label=await self.client.session.gtv(key='value'),
        )
        self.dd_output_method = Dropdown(
            label=await self.client.session.gtv(key='requisite_create_output_method'),
            on_change=self.change_output_method,
        )
        self.dd_output_requisite_data = Dropdown(
            label=await self.client.session.gtv(key='requisite_create_output_requisite_data'),
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
        )
        self.tf_output_currency_value_min = TextField(
            label=await self.client.session.gtv(key='value_min'),
            expand=1,
        )
        self.tf_output_currency_value_max = TextField(
            label=await self.client.session.gtv(key='value_max'),
            expand=1,
        )
        self.tf_output_rate = TextField(
            label=await self.client.session.gtv(key='rate'),
            expand=True,
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
                Container(
                    content=ExpansionTile(
                        title=Text(
                            value=await self.client.session.gtv(key='requisite_create_extra_options'),
                            size=settings.get_font_size(multiple=2.5),
                            font_family=Fonts.BOLD,
                            color=colors.ON_BACKGROUND,
                        ),
                        maintain_state=True,
                        controls=[
                            Row(
                                controls=[
                                    self.tf_output_currency_value_min,
                                    self.tf_output_currency_value_max,
                                ],
                                spacing=10,
                            ),
                        ],
                        bgcolor=colors.BACKGROUND,
                        collapsed_bgcolor=colors.BACKGROUND,
                        icon_color=colors.ON_BACKGROUND,
                        collapsed_icon_color=colors.ON_BACKGROUND,
                        initially_expanded=self.client.session.debug,
                    ),
                    border=border.all(color=colors.ON_BACKGROUND, width=1),
                ),
                self.tf_output_rate,
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
        await self.update_output(update=False)
        await self.update_subtitle(update=False)
        self.optional_container = Container(content=None)
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='requisite_create_title'),
            with_expand=True,
            main_section_controls=[
                self.dialog,
                Container(
                    content=Column(
                        controls=[
                            self.general_column,
                            self.optional_container
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
                                    value=await self.client.session.gtv(key='requisite_create_title'),
                                    size=settings.get_font_size(multiple=1.5),
                                ),
                                on_click=self.requisite_create,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
            ],
        )

    async def change_input_flex_btn(self, _=None):
        if self.btn_input_flex.value:
            self.tf_input_rate.value = None
            self.tf_input_rate.disabled = True
        else:
            self.tf_input_rate.disabled = False
        await self.tf_input_rate.update_async()

    async def change_type_currency(self, _=None):
        await self.update_subtitle(update=False)
        if not self.dd_type.value or not self.dd_currency.value:
            self.optional_container.content = None
            await self.optional_container.update_async()
            return
        currency = self.dd_currency.value
        if self.dd_type.value == RequisiteTypes.INPUT:
            self.optional_container.content = self.input_column
            await self.optional_container.update_async()
            self.dd_input_method.change_options(options=await self.get_method_options(currency_id_str=currency))
        elif self.dd_type.value == RequisiteTypes.OUTPUT:
            self.optional_container.content = self.output_column
            await self.optional_container.update_async()
            self.dd_output_method.change_options(options=await self.get_method_options(currency_id_str=currency))
            await self.change_output_method()
        await self.optional_container.update_async()

    async def change_output_method(self, update: bool = True, _=None):
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
        self.dd_output_requisite_data.change_options(options=options)
        if update:
            await self.dd_output_requisite_data.update_async()

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
                                size=settings.get_font_size(multiple=1.5),
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
        # check exists type
        if not self.dd_type.value:
            await self.set_type(loading=False)
            self.dd_type.error_text = await self.client.session.gtv(key='error_empty')
            await self.dd_type.update_async()
        type_ = self.dd_type.value
        # check exists currency
        if not self.dd_currency.value:
            await self.set_type(loading=False)
            self.dd_currency.error_text = await self.client.session.gtv(key='error_empty')
            await self.dd_currency.update_async()
        currency = await self.client.session.api.client.currencies.get(id_str=self.dd_currency.value)
        wallet_id = self.dd_wallet.value
        is_flex = False
        input_value, input_rate_value, output_rate_value, output_value = None, None, None, None
        if self.tf_input_value.value:
            input_value = self.tf_input_value.value
        if self.tf_input_rate.value:
            input_rate_value = self.tf_input_rate.value
        if self.tf_output_rate.value:
            output_rate_value = self.tf_output_rate.value
        if self.tf_output_value.value:
            output_value = self.tf_output_value.value
        input_method_id, output_requisite_data_id = None, None
        currency_value, rate, value = None, None, None
        currency_value_min, currency_value_max = None, None
        final_check_list = []
        if type_ == RequisiteTypes.INPUT:
            # write is_flex
            if self.btn_input_flex.value:
                is_flex = True
            # check float input value
            if not await Error.check_field(self, self.tf_input_value, check_float=True):
                await self.set_type(loading=False)
                return
            # check float rate
            if not is_flex:
                if not await Error.check_field(self, self.tf_input_rate, check_float=True):
                    await self.set_type(loading=False)
                    return
            # check exists input method
            if not self.dd_input_method.value:
                await self.set_type(loading=False)
                self.dd_input_method.error_text = await self.client.session.gtv(key='error_empty')
                await self.dd_input_method.update_async()
                return
            input_method_id = self.dd_input_method.value
            # check min/max currency value
            for field in [self.tf_input_currency_value_min, self.tf_input_currency_value_max]:
                if not field.value:
                    continue
                if not await Error.check_field(self, field, check_float=True):
                    await self.set_type(loading=False)
                    return
            # move to int all params
            currency_value = value_to_int(value=input_value, decimal=currency.decimal)
            rate = value_to_int(value=input_rate_value, decimal=currency.rate_decimal)
            currency_value_min = value_to_int(value=self.tf_input_currency_value_min.value, decimal=currency.decimal)
            currency_value_max = value_to_int(value=self.tf_input_currency_value_max.value, decimal=currency.decimal)
            # create final check list
            final_check_list = [
                (currency_value, self.tf_input_value, currency),
                (currency_value_min, self.tf_input_currency_value_min, currency),
                (currency_value_max, self.tf_input_currency_value_max, currency),
            ]
        elif type_ == RequisiteTypes.OUTPUT:
            # check float output value
            if not await Error.check_field(self, self.tf_output_value, check_float=True):
                await self.set_type(loading=False)
                return
            # check float rate
            if not await Error.check_field(self, self.tf_output_rate, check_float=True):
                await self.set_type(loading=False)
                return
            # check exists output requisite data and output method
            if not self.dd_output_requisite_data.value:
                await self.set_type(loading=False)
                self.dd_output_requisite_data.error_text = await self.client.session.gtv(key='error_empty')
                await self.dd_output_requisite_data.update_async()
                return
            output_requisite_data_id = self.dd_output_requisite_data.value
            if not self.dd_output_method.value:
                await self.set_type(loading=False)
                self.dd_output_method.error_text = await self.client.session.gtv(key='error_empty')
                await self.dd_output_method.update_async()
                return
            output_method_id = self.dd_output_method.value
            # check min/max currency value
            for field in [self.tf_output_currency_value_min, self.tf_output_currency_value_max]:
                if not field.value:
                    continue
                if not await Error.check_field(self, field, check_float=True):
                    await self.set_type(loading=False)
                    return
            # move to int all params
            currency_value = value_to_int(value=output_value, decimal=currency.decimal)
            rate = value_to_int(value=output_rate_value, decimal=currency.rate_decimal)
            currency_value_min = value_to_int(value=self.tf_output_currency_value_min.value, decimal=currency.decimal)
            currency_value_max = value_to_int(value=self.tf_output_currency_value_max.value, decimal=currency.decimal)
            # create final check list
            final_check_list = [
                (currency_value, self.tf_output_value, currency),
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
                currency_value_min=currency_value_min,
                currency_value_max=currency_value_max,
                is_flex=is_flex,
            )
            await self.set_type(loading=False)
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
