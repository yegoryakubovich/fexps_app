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

from flet_core import padding, ScrollMode, Row, Column, Container, KeyboardType, ControlEvent, AlertDialog, colors, \
    Image
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.input import Dropdown, TextField
from app.controls.layout import ClientBaseView
from app.utils import Icons
from app.utils.value import value_to_int
from app.views.client.account.requisite_data.models import RequisiteDataCreateModel
from fexps_api_client.utils import ApiException


class RequisiteTypes:
    input = 'input'
    output = 'output'


class RequisiteCreateView(ClientBaseView):
    route = '/client/requisites/create'

    methods = list[dict]
    dialog: AlertDialog

    # fields
    dd_type: Dropdown
    dd_wallet: Dropdown
    dd_currency: Dropdown
    dd_input_method: Dropdown = None
    dd_output_requisite_data: Dropdown = None
    requisite_data_model: RequisiteDataCreateModel
    tf_currency_value: TextField
    tf_currency_value_min: TextField
    tf_currency_value_max: TextField
    tf_value: TextField
    tf_value_min: TextField
    tf_value_max: TextField
    tf_rate: TextField

    optional: Column

    async def build(self):
        self.dialog = AlertDialog(modal=False)
        self.methods = await self.client.session.api.client.methods.get_list()
        type_options = [
            Option(
                text=await self.client.session.gtv(key=f'requisite_type_{type_}'),
                key=type_,
            )
            for type_ in [RequisiteTypes.input, RequisiteTypes.output]
        ]
        wallets_options = [
            Option(
                key=wallet.id, text=f'#{wallet.id} - {wallet.name}'
            )
            for wallet in await self.client.session.api.client.wallets.get_list()
        ]
        currency_options = [
            Option(
                text=currency.id_str.upper(),
                key=currency.id_str,
            )
            for currency in await self.client.session.api.client.currencies.get_list()
        ]
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
        self.dd_currency = Dropdown(
            label=await self.client.session.gtv(key='currency'),
            options=currency_options,
            on_change=self.change_type_or_currency,
        )
        self.optional = Column(controls=[])
        self.controls_container = Container(
            content=Column(
                controls=[
                    self.dialog,
                    self.dd_type,
                    self.dd_wallet,
                    self.dd_currency,
                    self.optional,
                    Row(
                        controls=[
                            StandardButton(
                                text=await self.client.session.gtv(key='requisite_create_title'),
                                on_click=self.requisite_create,
                                expand=True,
                            ),
                        ],
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
            title=await self.client.session.gtv(key='requisite_create_title'),
            main_section_controls=controls,
        )

    async def change_type_or_currency(self, _):
        async def get_input_method():
            input_method_options = []
            for method in self.methods:
                if method.currency.lower() != self.dd_currency.value.lower():
                    continue
                name = await self.client.session.gtv(key=method.name_text)
                input_method_options.append(Option(
                    text=f'{name} ({method.id})',
                    key=method.id,
                ))
            return Dropdown(
                label=await self.client.session.gtv(key='method'),
                options=input_method_options,
            )

        async def get_output_requisite_data():
            requisites_datas = await self.client.session.api.client.requisites_datas.get_list()
            output_requisite_data_options = []
            for requisite_data in requisites_datas:
                if requisite_data.currency.lower() != self.dd_currency.value.lower():
                    continue
                output_requisite_data_options.append(Option(
                    text=f'{requisite_data.name}',
                    key=requisite_data.id,
                ))
            return Dropdown(
                label=await self.client.session.gtv(key='output_requisite_data'),
                options=output_requisite_data_options,
                expand=True,
            )

        self.optional.controls = []
        if not self.dd_type.value or not self.dd_currency.value:
            await self.update_async()
            return
        if not self.dd_type.value:
            return
        if self.dd_type.value == RequisiteTypes.input:
            self.dd_input_method = await get_input_method()
            self.optional.controls += [
                self.dd_input_method,
            ]
        elif self.dd_type.value == RequisiteTypes.output:
            self.dd_output_requisite_data = await get_output_requisite_data()
            self.optional.controls += [
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
        self.tf_currency_value = TextField(
            label=await self.client.session.gtv(key='currency_value'),
            keyboard_type=KeyboardType.NUMBER,
        )
        self.tf_currency_value_min = TextField(
            label=await self.client.session.gtv(key='currency_value_min'),
            keyboard_type=KeyboardType.NUMBER,
            expand=1,
        )
        self.tf_currency_value_max = TextField(
            label=await self.client.session.gtv(key='currency_value_max'),
            keyboard_type=KeyboardType.NUMBER,
            expand=1,
        )
        self.tf_value = TextField(
            label=await self.client.session.gtv(key='value'),
            keyboard_type=KeyboardType.NUMBER,
        )
        self.tf_value_min = TextField(
            label=await self.client.session.gtv(key='value_min'),
            keyboard_type=KeyboardType.NUMBER,
            expand=1,
        )
        self.tf_value_max = TextField(
            label=await self.client.session.gtv(key='value_max'),
            keyboard_type=KeyboardType.NUMBER,
            expand=1,
        )
        self.tf_rate = TextField(
            label=await self.client.session.gtv(key='rate'),
            keyboard_type=KeyboardType.NUMBER,
        )

        self.optional.controls += [
            self.tf_currency_value,
            Row(
                controls=[
                    self.tf_currency_value_min,
                    self.tf_currency_value_max,
                ],
            ),
            self.tf_value,
            Row(
                controls=[
                    self.tf_value_min,
                    self.tf_value_max,
                ],
            ),
            self.tf_rate,
        ]
        await self.update_async()

    async def create_output_requisite_data(self, _):
        self.requisite_data_model = RequisiteDataCreateModel(
            session=self.client.session,
            update_async=self.update_async,
            after_clise=self.create_output_requisite_data_after_close,
            before_clise=self.create_output_requisite_data_before_clise,
        )
        await self.requisite_data_model.build()
        self.dialog.content = Container(
            content=Column(
                controls=self.requisite_data_model.controls,
            ),
            height=self.requisite_data_model.height,
        )
        self.dialog.actions = self.requisite_data_model.buttons
        self.dialog.open = True
        await self.update_async()

    async def create_output_requisite_data_after_close(self):
        self.dialog.open = False
        await self.update_async()

    async def create_output_requisite_data_before_clise(self):
        await self.change_type_or_currency('')
        await self.update_async()
    async def requisite_create(self, _: ControlEvent):
        await self.set_type(loading=True)
        currency = await self.client.session.api.client.currencies.get(id_str=self.dd_currency.value)
        currency_value = value_to_int(
            value=self.tf_currency_value.value, decimal=currency.decimal,
        ) if self.tf_currency_value.value else None
        currency_value_min = value_to_int(
            value=self.tf_currency_value_min.value, decimal=currency.decimal,
        ) if self.tf_currency_value_min.value else None
        currency_value_max = value_to_int(
            value=self.tf_currency_value_max.value, decimal=currency.decimal,
        ) if self.tf_currency_value_max.value else None
        value = value_to_int(value=self.tf_value.value) if self.tf_value.value else None
        value_min = value_to_int(value=self.tf_value_min.value) if self.tf_value_min.value else None
        value_max = value_to_int(value=self.tf_value_max.value) if self.tf_value_max.value else None
        rate = value_to_int(
            value=self.tf_rate.value, decimal=currency.rate_decimal,
        ) if self.tf_rate.value else None
        try:
            await self.client.session.api.client.requisites.create(
                wallet_id=self.dd_wallet.value,
                type_=self.dd_type.value,
                input_method_id=self.dd_input_method.value if self.dd_input_method else None,
                output_requisite_data_id=self.dd_output_requisite_data.value if self.dd_output_requisite_data else None,
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
