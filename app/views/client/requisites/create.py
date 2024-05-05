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

from flet_core import ScrollMode, Row, Column, Container, AlertDialog, alignment, KeyboardType, Image, colors
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import SubTitle, Text
from app.controls.input import Dropdown, TextField
from app.controls.layout import ClientBaseView
from app.utils import Icons, Fonts
from app.views.client.account.requisite_data.models import RequisiteDataCreateModel
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
    tf_input_value_min = TextField
    tf_input_value_max = TextField
    dd_input_method: Dropdown
    # output
    output_column: Column
    output_subtitle_text: Text
    tf_output_value: TextField
    tf_output_value_min = TextField
    tf_output_value_max = TextField
    dd_output_method: Dropdown
    dd_output_requisite_data: Dropdown

    async def get_method_options(self, currency_id_str: str) -> list[Option]:
        options = []
        for method in self.methods:
            if method.currency.id_str.lower() != currency_id_str.lower():
                continue
            options += [
                Option(text=f'{await self.client.session.gtv(key=method.name_text)} ({method.id})', key=method.id),
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
            value=await self.client.session.gtv(key='requisite_create_input', currency=''),
            size=24,
            font_family=Fonts.BOLD,
            color=colors.ON_BACKGROUND,
        )
        self.tf_input_value = TextField(
            label=await self.client.session.gtv(key='value'),
            keyboard_type=KeyboardType.NUMBER,
        )
        self.tf_input_value_min = TextField(
            label=await self.client.session.gtv(key='value_min'),
            keyboard_type=KeyboardType.NUMBER,
            expand=1,
        )
        self.tf_input_value_max = TextField(
            label=await self.client.session.gtv(key='value_max'),
            keyboard_type=KeyboardType.NUMBER,
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
                Row(
                    controls=[
                        self.tf_input_value_min,
                        self.tf_input_value_max,
                    ],
                    spacing=16,
                ),
                self.dd_input_method,
            ],
        )
        if update:
            await self.input_column.update_async()

    async def update_output(self, update: bool = True) -> None:
        self.output_subtitle_text = Text(
            value=await self.client.session.gtv(key='requisite_create_output', currency=''),
            size=24,
            font_family=Fonts.BOLD,
            color=colors.ON_BACKGROUND,
        )
        self.tf_output_value = TextField(
            label=await self.client.session.gtv(key='value'),
            keyboard_type=KeyboardType.NUMBER,
        )
        self.tf_output_value_min = TextField(
            label=await self.client.session.gtv(key='value_min'),
            keyboard_type=KeyboardType.NUMBER,
            expand=1,
        )
        self.tf_output_value_max = TextField(
            label=await self.client.session.gtv(key='value_max'),
            keyboard_type=KeyboardType.NUMBER,
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
        self.output_column = Column(
            controls=[
                Row(
                    controls=[
                        self.output_subtitle_text,
                    ],
                ),
                self.tf_output_value,
                Row(
                    controls=[
                        self.tf_output_value_min,
                        self.tf_output_value_max,
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
                    ],
                ),
            ],
        )
        if update:
            await self.output_column.update_async()

    async def construct(self):
        self.dialog = AlertDialog(modal=False)
        await self.set_type(loading=True)
        self.methods = await self.client.session.api.client.methods.get_list()
        self.currencies = await self.client.session.api.client.currencies.get_list()
        await self.set_type(loading=False)
        await self.update_general(update=False)
        await self.update_input(update=False)
        await self.update_output(update=False)
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

    async def change_type_currency(self, _):
        if not self.dd_type.value or not self.dd_currency.value:
            self.dd_input_method.value, self.dd_input_method.disabled = None, True
            self.dd_output_method.value, self.dd_output_method.disabled = None, True
            self.dd_output_requisite_data.value, self.dd_output_requisite_data.disabled = None, True
            self.input_subtitle_text = Text(
                value=await self.client.session.gtv(key='requisite_create_input', currency=''),
                size=24,
                font_family=Fonts.BOLD,
                color=colors.ON_BACKGROUND,
            )
            self.output_subtitle_text = Text(
                value=await self.client.session.gtv(key='requisite_create_output', currency=''),
                size=24,
                font_family=Fonts.BOLD,
                color=colors.ON_BACKGROUND,
            )
            await self.update_async()
            return
        currency = self.dd_currency.value
        if self.dd_type.value == RequisiteTypes.INPUT:
            self.input_subtitle_text = Text(
                value=await self.client.session.gtv(key='requisite_create_input', currency=currency.upper()),
                size=24,
                font_family=Fonts.BOLD,
                color=colors.ON_BACKGROUND,
            )
            self.dd_input_method.options = await self.get_method_options(currency_id_str=currency)
            self.dd_input_method.disabled = False
        elif self.dd_type.value == RequisiteTypes.OUTPUT:
            self.output_subtitle_text = Text(
                value=await self.client.session.gtv(key='requisite_create_output', currency=currency.upper()),
                size=24,
                font_family=Fonts.BOLD,
                color=colors.ON_BACKGROUND,
            )
            self.dd_output_method.options = await self.get_method_options(currency_id_str=currency)
            self.dd_output_method.disabled = False
            self.dd_output_requisite_data.value, self.dd_output_requisite_data.disabled = None, True
        await self.update_async()

    async def change_output_method(self, _):
        if not self.dd_output_method or not self.dd_output_method.value:
            return
        await self.set_type(loading=True)
        requisites_datas = await self.client.session.api.client.requisites_datas.get_list()
        options = []
        for requisite_data in requisites_datas:
            if int(requisite_data.method.id) != int(self.dd_output_method.value):
                continue
            options += [
                Option(text=f'{requisite_data.name}', key=requisite_data.id)
            ]
        self.dd_output_requisite_data.disabled = False
        self.dd_output_requisite_data.options = options
        await self.set_type(loading=False)

    async def create_output_requisite_data(self, _):
        if self.dd_type.value != RequisiteTypes.OUTPUT:
            return
        self.requisite_data_model = RequisiteDataCreateModel(
            session=self.client.session,
            update_async=self.update_async,
            before_close=self.create_output_requisite_data_before_close,
            after_close=self.create_output_requisite_data_after_close,
            currency_id_str=self.dd_currency.value,
            method_id=self.dd_output_method.value,
        )
        await self.requisite_data_model.construct()
        self.dialog.content = Container(
            content=Column(
                controls=self.requisite_data_model.controls,
            ),
            expand=True,
            width=self.requisite_data_model.width,
        )
        self.dialog.actions = self.requisite_data_model.buttons
        self.dialog.open = True
        await self.update_async()

    async def create_output_requisite_data_before_close(self):
        self.dialog.open = False
        await self.update_async()

    async def create_output_requisite_data_after_close(self):
        await self.change_output_method('')
        if self.dd_currency.value == self.requisite_data_model.currency_id_str:
            if str(self.dd_output_method.value) == str(self.requisite_data_model.method_id):
                self.dd_output_requisite_data.value = self.requisite_data_model.requisite_data_id
        await self.update_async()

    async def requisite_create(self, _):
        type_ = self.dd_type.value
        for field in [self.dd_type, self.dd_currency, self.tf_input_value, self.tf_output_value]:
            if field.value is not None:
                continue
            field.error_text = await self.client.session.gtv(key='error_empty')
            await self.update_async()
            return
        wallet_id = self.dd_wallet.value
        input_method_id = None
        output_requisite_data_id = None
        currency_value = self.tf_input_value.value
        currency_value_min = None
        currency_value_max = None
        value = self.tf_output_value.value
        value_min = None
        value_max = None
        rate = None
        if type_ == RequisiteTypes.INPUT:
            for field in [self.dd_input_method]:
                if field.value is not None:
                    continue
                field.error_text = await self.client.session.gtv(key='error_empty')
                await self.update_async()
                return
            input_method_id = self.dd_input_method.value
            if self.tf_input_value_min.value:
                currency_value_min = self.tf_input_value_min.value
            if self.tf_input_value_max.value:
                currency_value_max = self.tf_input_value_max.value
            if self.tf_output_value_min.value:
                value_min = self.tf_output_value_min.value
            if self.tf_output_value_max.value:
                value_max = self.tf_output_value_max.value
        elif type_ == RequisiteTypes.OUTPUT:
            for field in [self.dd_output_method, self.dd_output_requisite_data]:
                if field.value is not None:
                    continue
                field.error_text = await self.client.session.gtv(key='error_empty')
                await self.update_async()
                return
            output_requisite_data_id = self.dd_output_requisite_data.value
            if self.tf_input_value_min.value:
                value_min = self.tf_input_value_min.value
            if self.tf_input_value_max.value:
                value_max = self.tf_input_value_max.value
            if self.tf_output_value_min.value:
                currency_value_min = self.tf_output_value_min.value
            if self.tf_output_value_max.value:
                currency_value_max = self.tf_output_value_max.value
        try:
            await self.client.session.api.client.requisites.create(
                type_=type_,
                wallet_id=wallet_id,
                input_method_id=input_method_id,
                output_requisite_data_id=output_requisite_data_id,
                currency_value=currency_value,
                currency_value_min=currency_value_min,
                currency_value_max=currency_value_max,
                value=value,
                value_min=value_min,
                value_max=value_max,
                rate=rate,
            )
            await self.set_type(loading=False)
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
