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

from flet_core import Row, colors, MainAxisAlignment, Image, Column, ScrollMode, Container, AlertDialog, padding, \
    Divider

from app.controls.button import StandardButton
from app.controls.information import SubTitle, Text, InformationContainer
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Icons, Fonts, value_to_float, Error, value_to_int, value_to_str
from app.utils.constants.order import OrderStates
from app.utils.value import requisite_value_to_str, get_fix_rate
from app.views.client.requisites.orders.get import RequisiteOrderView
from config import settings
from fexps_api_client.utils import ApiException


class RequisiteView(ClientBaseView):
    route = '/client/requisite/get'

    requisite = dict
    orders = list[dict]

    dialog: AlertDialog
    tf_currency_value: TextField

    info_card: InformationContainer
    orders_row: Row
    update_value_button: StandardButton
    enable_button: StandardButton
    stop_button: StandardButton
    disable_button: StandardButton

    def __init__(self, requisite_id: int):
        super().__init__()
        self.requisite_id = requisite_id

    """
    INFO CARD
    """

    async def update_info_card(self, update: bool = True) -> None:
        info_card_controls = [
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='requisite_id'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=f'{self.requisite.id:08}',
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='type'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=await self.client.session.gtv(key=f'requisite_type_{self.requisite.type}'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='state'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=await self.client.session.gtv(key=f'requisite_state_{self.requisite.state}'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='requisite_is_flex'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=await self.client.session.gtv(key=f'requisite_is_flex_{self.requisite.is_flex}'.lower()),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            Divider(color=colors.ON_PRIMARY_CONTAINER),
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='currency'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=self.requisite.currency.id_str.upper(),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]
        currency_value = value_to_str(
            value=value_to_float(value=self.requisite.currency_value, decimal=self.requisite.currency.decimal),
        )
        total_currency_value = value_to_str(
            value=value_to_float(value=self.requisite.total_currency_value, decimal=self.requisite.currency.decimal),
        )
        info_card_controls += [
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='currency_value'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=f'{currency_value}/{total_currency_value}',
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]
        if self.requisite.rate:
            rate_str = value_to_str(
                value=get_fix_rate(
                    rate=value_to_float(value=self.requisite.rate, decimal=self.requisite.currency.rate_decimal),
                ),
            )
            info_card_controls += [
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='rate'),
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                        Text(
                            value=rate_str,
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
            ]
        if self.requisite.input_method:
            info_card_controls += [
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='requisite_method'),
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                        Text(
                            value=await self.client.session.gtv(key=self.requisite.input_method.name_text),
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
            ]
        if self.requisite.output_requisite_data:
            info_card_controls += [
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='requisite_method'),
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                        Text(
                            value=await self.client.session.gtv(key=self.requisite.output_method.name_text),
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                *[
                    Row(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key=field_scheme['name_text_key']),
                                size=settings.get_font_size(multiple=1.5),
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                            Text(
                                value=self.requisite.output_requisite_data.fields[field_scheme['key']],
                                size=settings.get_font_size(multiple=1.5),
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    )
                    for field_scheme in self.requisite.output_method.schema_fields
                ],
            ]
        self.info_card = InformationContainer(
            content=Column(
                controls=info_card_controls,
                spacing=-50,
            ),
            bgcolor=colors.PRIMARY_CONTAINER,
            padding=padding.symmetric(vertical=32, horizontal=32),
        )
        if update:
            await self.info_card.update_async()

    """
    ORDERS
    """

    async def get_orders_cards(self):
        cards: list = []
        for order in self.orders:
            currency = order.currency
            requisite_data_str = ', '.join([
                value_
                for key_, value_ in order.requisite_fields.items()
            ])
            state_str = await self.client.session.gtv(key=f'requisite_order_{order.type}_{order.state}')
            value = value_to_float(value=order.currency_value, decimal=currency.decimal)
            value_str = f'{value} {currency.id_str.upper()}'
            color, bgcolor = colors.ON_PRIMARY, colors.PRIMARY
            if order.state in [OrderStates.COMPLETED, OrderStates.CANCELED]:
                color, bgcolor = colors.ON_PRIMARY_CONTAINER, colors.PRIMARY_CONTAINER
            order_info_str = ''
            if order.requisite_scheme_fields:
                order_info_key = order.requisite_scheme_fields[0]['key']
                order_info_str = requisite_value_to_str(
                    value=order.requisite_fields[order_info_key],
                    card_number_replaces=True,
                )
            cards.append(
                StandardButton(
                    content=Row(
                        controls=[
                            Column(
                                controls=[
                                    Row(
                                        controls=[
                                            Text(
                                                value=f'#{order.id:08}',
                                                size=settings.get_font_size(multiple=1.2),
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                            Text(
                                                value='|',
                                                size=settings.get_font_size(multiple=1.2),
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                            Text(
                                                value=requisite_data_str,
                                                size=settings.get_font_size(multiple=1.2),
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=state_str,
                                                size=settings.get_font_size(multiple=1.5),
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=order_info_str,
                                                size=settings.get_font_size(multiple=2),
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=value_str,
                                                size=settings.get_font_size(multiple=1.5),
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                ],
                                expand=True,
                            ),
                            Image(
                                src=Icons.OPEN,
                                height=28,
                                color=color,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        spacing=2,
                    ),
                    on_click=partial(self.order_view, order.id),
                    bgcolor=bgcolor,
                ),
            )
        return cards

    async def update_order_row(self, update: bool = True) -> None:
        self.orders_row = Row(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='requisite_orders_title')),
                *await self.get_orders_cards(),
            ],
            wrap=True,
        )
        if update:
            await self.orders_row.update_async()

    """
    BUTTON
    """

    async def update_enable_button(self, update: bool = True) -> None:
        self.enable_button = StandardButton(
            content=Text(
                value=await self.client.session.gtv(key='requisite_enable_button'),
                size=settings.get_font_size(multiple=1.5),
                font_family=Fonts.SEMIBOLD,
                color=colors.BLACK,
            ),
            bgcolor=colors.GREEN,
            on_click=self.requisite_state_enable,
            expand=1,
        )
        if update:
            await self.enable_button.update_async()

    async def update_update_value_button(self, update: bool = True) -> None:
        self.update_value_button = StandardButton(
            content=Text(
                value=await self.client.session.gtv(key='requisite_update_value_button'),
                size=settings.get_font_size(multiple=1.5),
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY,
            ),
            bgcolor=colors.PRIMARY,
            on_click=self.requisite_update_value_open,
            expand=1,
        )
        if update:
            await self.update_value_button.update_async()

    async def update_stop_button(self, update: bool = True) -> None:
        self.stop_button = StandardButton(
            content=Text(
                value=await self.client.session.gtv(key='requisite_stop_button'),
                size=settings.get_font_size(multiple=1.5),
                font_family=Fonts.SEMIBOLD,
                color=colors.BLACK,
            ),
            bgcolor=colors.RED,
            on_click=self.requisite_state_stop,
            expand=1,
        )
        if update:
            await self.stop_button.update_async()

    async def update_disable_button(self, update: bool = True) -> None:
        self.disable_button = StandardButton(
            content=Text(
                value=await self.client.session.gtv(key='requisite_disable_button'),
                size=settings.get_font_size(multiple=1.5),
                font_family=Fonts.SEMIBOLD,
                color=colors.BLACK,
            ),
            bgcolor=colors.RED,
            on_click=self.requisite_state_disable,
            expand=1,
        )
        if update:
            await self.disable_button.update_async()

    async def construct(self):
        self.dialog = AlertDialog(modal=False)
        controls, buttons = [], []
        await self.set_type(loading=True)
        self.requisite = await self.client.session.api.client.requisites.get(id_=self.requisite_id)
        self.orders = await self.client.session.api.client.orders.list_get.by_requisite(requisite_id=self.requisite_id)
        await self.set_type(loading=False)
        await self.update_info_card(update=False)
        await self.update_order_row(update=False)
        controls += [
            self.info_card,
            self.orders_row,
        ]
        if self.requisite.state == 'enable':
            await self.update_update_value_button(update=False)
            await self.update_stop_button(update=False)
            buttons += [
                Row(
                    controls=[
                        self.update_value_button,
                    ],
                ),
                Row(
                    controls=[
                        self.stop_button,
                    ],
                ),
            ]
        elif self.requisite.state == 'stop':
            await self.update_update_value_button(update=False)
            await self.update_enable_button(update=False)
            await self.update_disable_button(update=False)
            buttons += [
                Row(
                    controls=[
                        self.update_value_button,
                    ],
                ),
                Row(
                    controls=[
                        self.disable_button,
                        self.enable_button,
                    ],
                ),
            ]
        title_str = await self.client.session.gtv(key='requisite_get_title')
        self.controls = await self.get_controls(
            title=f'{title_str} #{self.requisite.id:08}',
            with_expand=True,
            main_section_controls=[
                self.dialog,
                Container(
                    content=Column(
                        controls=controls,
                        scroll=ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                *[
                    Container(content=button)
                    for button in buttons
                ],
            ],
        )

    async def order_view(self, order_id: int, _):
        await self.client.change_view(view=RequisiteOrderView(order_id=order_id))

    async def requisite_update_value_open(self, _):
        self.tf_currency_value = TextField(
            label=await self.client.session.gtv(key='currency_value'),
            value=value_to_float(value=self.requisite.total_currency_value, decimal=self.requisite.currency.decimal),
        )
        self.dialog.content = Container(
            content=Column(
                controls=[
                    self.tf_currency_value,
                ],
                scroll=ScrollMode.AUTO,
            ),
            width=400,
        )
        self.dialog.actions = [
            Row(
                controls=[
                    StandardButton(
                        content=Text(
                            value=await self.client.session.gtv(key='confirm'),
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.REGULAR,
                        ),
                        on_click=self.requisite_update_value,
                        expand=True,
                    ),
                ],
            )
        ]
        self.dialog.open = True
        await self.dialog.update_async()

    async def requisite_update_value_close(self, _):
        self.dialog.open = False
        await self.dialog.update_async()

    async def requisite_update_value(self, _):
        if not await Error.check_field(self, self.tf_currency_value, check_float=True):
            await self.tf_currency_value.update_async()
            return
        currency_value = value_to_int(value=self.tf_currency_value.value, decimal=self.requisite.currency.decimal)
        await self.requisite_update_value_close(_)
        try:
            await self.client.session.api.client.requisites.updates.value(
                id_=self.requisite_id,
                currency_value=currency_value,
            )
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def requisite_state_stop(self, _):
        await self.set_type(loading=True)
        try:
            await self.client.session.api.client.requisites.updates.stop(id_=self.requisite_id)
            await self.set_type(loading=False)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)

    async def requisite_state_enable(self, _):
        await self.set_type(loading=True)
        try:
            await self.client.session.api.client.requisites.updates.enable(id_=self.requisite_id)
            await self.set_type(loading=False)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)

    async def requisite_state_disable(self, _):
        await self.set_type(loading=True)
        try:
            await self.client.session.api.client.requisites.updates.disable(id_=self.requisite_id)
            await self.set_type(loading=False)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
