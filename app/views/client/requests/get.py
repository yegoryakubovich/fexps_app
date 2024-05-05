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

from flet_core import Column, colors, Row, MainAxisAlignment, Container, \
    padding, Image, Divider, UserControl, AlertDialog, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text, SubTitle, InformationContainer
from app.controls.layout import ClientBaseView
from app.utils import Fonts, value_to_float, Icons, value_to_str
from app.utils.value import requisite_value_to_str, get_fix_rate, get_input_currency_value, get_input_value, \
    get_output_currency_value, get_output_value
from app.views.client.requests.models import RequestUpdateNameModel
from app.views.client.requests.orders.get import RequestOrderView
from app.views.main.tabs.acoount import open_support
from fexps_api_client.utils import ApiException


class DynamicTimer(UserControl):
    time_text: Text

    def __init__(self, seconds: int):
        super().__init__()
        self.running = True
        self.seconds = seconds

    def did_mount(self):
        asyncio.create_task(self.update_second())

    def will_unmount(self):
        self.running = False

    def get_time(self):
        seconds = self.seconds
        minutes = 0
        while seconds >= 60:
            seconds -= 60
            minutes += 1
        return f'{minutes:02}:{seconds:02}'

    async def update_second(self):
        while self.seconds and self.running:
            self.time_text.value = self.get_time()
            await self.time_text.update_async()
            await asyncio.sleep(1)
            self.seconds -= 1

    def build(self):
        self.time_text = Text(
            value='',
            size=16,
            font_family=Fonts.BOLD,
        )
        return self.time_text


class RequestView(ClientBaseView):
    route = '/client/request/get'
    dialog: AlertDialog

    request_edit_name_model: RequestUpdateNameModel
    request = dict
    orders = list[dict]

    info_card: InformationContainer
    waiting_button: StandardButton
    orders_row: Row
    help_column: Column

    def __init__(self, request_id: int):
        super().__init__()
        self.request_id = request_id
        self.reload_bool = False
        self.reload_stop = False
        self.dialog = AlertDialog(modal=True)

    async def update_info_card(self, update: bool = True) -> None:
        rate = value_to_float(value=self.request.rate, decimal=self.request.rate_decimal)
        rate_str = ''
        if self.request.type == 'input':
            input_currency = self.request.input_currency
            input_currency_value = value_to_float(
                value=get_input_currency_value(request=self.request),
                decimal=input_currency.decimal,
            )
            input_value = value_to_float(
                value=get_input_value(request=self.request),
                decimal=input_currency.decimal,
            )
            value_str = (
                f'{value_to_str(value=input_currency_value)} {input_currency.id_str.upper()}'
                f' -> '
                f'{value_to_str(value=input_value)}'
            )
            if rate:
                rate_fix, rate_decimal = get_fix_rate(rate=rate)
                rate_str = (
                    f'{rate_fix} {input_currency.id_str.upper()}'
                    f' / '
                    f'{rate_decimal}'
                )
        elif self.request.type == 'output':
            output_currency = self.request.output_currency
            output_currency_value = value_to_float(
                value=get_output_currency_value(request=self.request),
                decimal=output_currency.decimal,
            )
            output_value = value_to_float(
                value=get_output_value(request=self.request),
                decimal=output_currency.decimal,
            )
            value_str = (
                f'{value_to_str(value=output_value)}'
                f' -> '
                f'{value_to_str(value=output_currency_value)} {output_currency.id_str.upper()}'
            )
            if rate:
                rate_fix, rate_decimal = get_fix_rate(rate=rate)
                rate_str = (
                    f'{rate_fix} {output_currency.id_str.upper()}'
                    f' / '
                    f'{rate_decimal}'
                )
        else:
            input_currency = self.request.input_currency
            output_currency = self.request.output_currency
            input_currency_value = value_to_float(
                value=get_input_currency_value(request=self.request),
                decimal=input_currency.decimal,
            )
            output_currency_value = value_to_float(
                value=get_output_currency_value(request=self.request),
                decimal=output_currency.decimal,
            )
            value_str = (
                f'{value_to_str(value=input_currency_value)} {input_currency.id_str.upper()}'
                f' -> '
                f'{value_to_str(value=output_currency_value)} {output_currency.id_str.upper()}'
            )
            if rate:
                rate_fix, rate_decimal = get_fix_rate(rate=rate)
                rate_str = (
                    f'{rate_fix} {input_currency.id_str.upper()}'
                    f' / '
                    f'{rate_decimal} {output_currency.id_str.upper()}'
                )
        if self.request.name:
            value_str = f'{self.request.name} ({value_str})'
        state_row = await self.client.session.gtv(key=f'request_state_{self.request.state}')
        info_card_controls = []
        info_card_controls += [
            Row(
                controls=[
                    Text(
                        value=value_str,
                        size=28,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    StandardButton(
                        content=Image(
                            src=Icons.EDIT,
                            color=colors.ON_PRIMARY_CONTAINER,
                            height=24,
                            width=24,
                        ),
                        horizontal=0,
                        vertical=0,
                        bgcolor=colors.PRIMARY_CONTAINER,
                        on_click=self.request_edit_name,
                    ),
                ],
                wrap=True,
            ),
            Divider(color=colors.ON_PRIMARY_CONTAINER),
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_id'),
                        size=14,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=f'{self.request.id:08}',
                        size=14,
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
                        size=14,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=state_row,
                        size=14,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='rate'),
                        size=14,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=rate_str,
                        size=14,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]
        if self.request.input_method:
            info_card_controls += [
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='request_input_method'),
                            size=14,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                        Text(
                            value=await self.client.session.gtv(key=self.request.input_method.name_text),
                            size=14,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
            ]
        if self.request.output_method:
            info_card_controls += [
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='request_output_method'),
                            size=14,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                        Text(
                            value=await self.client.session.gtv(key=self.request.output_method.name_text),
                            size=14,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
            ]
        info_card_controls += [
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='date'),
                        size=14,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=self.request.date.strftime('%Y-%m-%d, %H:%M:%S'),
                        size=14,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
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

    async def update_waiting_button(self, update: bool = True) -> None:
        self.waiting_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_confirm'),
                        size=16,
                        font_family=Fonts.BOLD,
                    ),
                    DynamicTimer(seconds=self.request.waiting_delta),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            on_click=self.waiting_confirm,
            expand=1,
        )
        if update:
            await self.waiting_button.update_async()

    """
    ORDERS SEND
    """

    async def get_orders_cards(self, type_: str):
        cards: list = []
        for order in self.orders:
            if order.type != type_:
                continue
            currency = order.currency
            state_str = await self.client.session.gtv(key=f'request_order_{order.type}_{order.state}')
            value = value_to_float(value=order.currency_value, decimal=currency.decimal)
            value_str = f'{value} {currency.id_str.upper()}'
            color, bgcolor = colors.ON_PRIMARY, colors.PRIMARY
            if order.state in ['completed', 'canceled']:
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
                                                value=state_str,
                                                size=12,
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=order_info_str,
                                                size=28,
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=value_str,
                                                size=16,
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

    async def update_orders_row(self, update: bool = True) -> None:
        controls = []
        input_orders = await self.get_orders_cards(type_='input')
        if input_orders:
            controls += [
                SubTitle(value=await self.client.session.gtv(key='request_orders_input_title')),
                *input_orders,
            ]
        output_orders = await self.get_orders_cards(type_='output')
        if output_orders:
            controls += [
                SubTitle(value=await self.client.session.gtv(key='request_orders_output_title')),
                *output_orders,
            ]
        self.orders_row = Row(
            controls=controls,
            wrap=True,
        )
        if update:
            await self.orders_row.update_async()

    async def update_help_column(self, update: bool = True) -> None:
        self.help_column = Column(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='request_help_title')),
                StandardButton(
                    content=Row(
                        controls=[
                            Row(
                                controls=[
                                    Text(
                                        value=await self.client.session.gtv(key='faq'),
                                        size=18,
                                        font_family=Fonts.SEMIBOLD,
                                        color=colors.ON_BACKGROUND,
                                    ),
                                ],
                                expand=True,
                            ),
                            Image(
                                src=Icons.OPEN,
                                height=18,
                                color=colors.ON_BACKGROUND,
                            ),
                        ],
                    ),
                    bgcolor=colors.BACKGROUND,
                    horizontal=0,
                    vertical=0,
                    on_click=None,
                ),
                StandardButton(
                    content=Row(
                        controls=[
                            Row(
                                controls=[
                                    Text(
                                        value=await self.client.session.gtv(key='help_telegram_contact_title'),
                                        size=18,
                                        font_family=Fonts.SEMIBOLD,
                                        color=colors.ON_BACKGROUND,
                                    ),
                                ],
                                expand=True,
                            ),
                            Image(
                                src=Icons.OPEN,
                                height=18,
                                color=colors.ON_BACKGROUND,
                            ),
                        ]
                    ),
                    bgcolor=colors.BACKGROUND,
                    horizontal=0,
                    vertical=0,
                    on_click=open_support,
                ),
            ],
        )
        if update:
            await self.help_column.update_async()

    async def construct(self):
        controls, buttons = [], []
        await self.set_type(loading=True)
        self.request = await self.client.session.api.client.requests.get(id_=self.request_id)
        self.orders = await self.client.session.api.client.orders.list_get.by_request(request_id=self.request_id)
        await self.set_type(loading=False)
        await self.update_info_card(update=False)
        controls += [
            self.info_card,
        ]
        if self.request.state == 'loading':
            pass
        elif self.request.state == 'waiting':
            await self.update_waiting_button(update=False)
            buttons += [
                Row(
                    controls=[
                        self.waiting_button,
                    ]
                ),
            ]
        else:
            await self.update_orders_row(update=False)
            await self.update_help_column(update=False)
            controls += [
                self.orders_row,
                self.help_column,
            ]
        title_str = await self.client.session.gtv(key='request_get_title')
        self.controls = await self.get_controls(
            title=f'{title_str} #{self.request.id:08}',
            with_expand=True,
            back_with_restart=True,
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

    async def request_edit_name(self, _):
        self.reload_stop = True
        self.request_edit_name_model = RequestUpdateNameModel(
            session=self.client.session,
            update_async=self.update_async,
            request_id=self.request.id,
            request_name=self.request.get('name'),
            before_close=self.edit_name_before,
            after_close=self.edit_name_after,
        )
        await self.request_edit_name_model.construct()
        self.dialog.content = Container(
            content=Column(
                controls=self.request_edit_name_model.controls,
            ),
            height=self.request_edit_name_model.height,
        )
        self.dialog.actions = self.request_edit_name_model.buttons
        self.dialog.open = True
        await self.update_async()

    async def edit_name_before(self):
        self.dialog.open = False
        await self.update_async()

    async def edit_name_after(self):
        self.reload_stop = False
        await self.construct()
        await self.update_async()

    async def order_view(self, order_id: int, _):
        await self.client.change_view(view=RequestOrderView(order_id=order_id))

    async def waiting_confirm(self, _):
        try:
            await self.client.session.api.client.requests.updates.confirmation(id_=self.request_id)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            return await self.client.session.error(exception=exception)
