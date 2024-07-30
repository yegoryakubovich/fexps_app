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
from typing import Optional

from flet_core import Column, colors, Row, MainAxisAlignment, Container, \
    padding, Image, Divider, UserControl, AlertDialog, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text, SubTitle, InformationContainer
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Fonts, value_to_float, Icons, value_to_str
from app.utils.constants.order import OrderStates, OrderTypes
from app.utils.constants.request import RequestStates, RequestTypes
from app.utils.value import requisite_value_to_str, get_fix_rate, value_replace
from app.views.client.requests.models import RequestUpdateNameModel
from app.views.client.requests.orders.get import RequestOrderView
from config import settings
from fexps_api_client.utils import ApiException


class DynamicTimer(UserControl):
    time_text: Text

    def __init__(
            self,
            seconds: int,
            font_size: int = settings.get_font_size(multiple=1.5),
            font_family=Fonts.BOLD,
            color=colors.BLACK,
    ):
        super().__init__()
        self.running = True
        self.seconds = seconds
        self.color = color
        self.font_size = font_size
        self.font_family = font_family

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
        return f'({minutes:02}:{seconds:02})'

    async def update_second(self):
        while self.seconds and self.running:
            self.time_text.value = self.get_time()
            await self.time_text.update_async()
            await asyncio.sleep(1)
            self.seconds -= 1
        self.time_text.color = colors.RED
        self.time_text.value = f'(X)'
        await self.time_text.update_async()

    def build(self):
        self.time_text = Text(
            value='',
            size=self.font_size,
            color=self.color,
            font_family=self.font_family,
        )
        return self.time_text


class RequestView(ClientBaseView):
    route = '/client/request/get'
    dialog: AlertDialog

    request_edit_name_model: RequestUpdateNameModel
    request = dict
    orders = list[dict]
    account_client_text = dict

    info_card: InformationContainer
    confirmation_timer: Optional[DynamicTimer]
    confirmation_false_button: StandardButton
    confirmation_true_button: StandardButton
    cancellation_button: StandardButton
    orders_row: Row
    client_text_column: Column

    def __init__(self, request_id: int):
        super().__init__()
        self.request_id = request_id
        self.dialog = AlertDialog(modal=True)
        self.confirmation_timer = None

    async def update_info_card(self, update: bool = True) -> None:
        rate = value_to_float(value=self.request.rate, decimal=self.request.rate_decimal)
        input_currency_id_str, output_currency_id_str = '', ''
        if self.request.type == RequestTypes.INPUT:
            input_currency = self.request.input_method.currency
            input_currency_id_str = input_currency.id_str.upper()
            input_value = value_to_float(
                value=self.request.input_currency_value,
                decimal=input_currency.decimal,
            )
            output_value = value_to_float(value=self.request.input_value)
        elif self.request.type == RequestTypes.OUTPUT:
            input_value = value_to_float(value=self.request.output_value)
            output_currency = self.request.output_method.currency
            output_currency_id_str = output_currency.id_str.upper()
            output_value = value_to_float(
                value=self.request.output_currency_value,
                decimal=output_currency.decimal,
            )
        else:
            input_currency = self.request.input_method.currency
            input_currency_id_str = input_currency.id_str.upper()
            input_value = value_to_float(
                value=self.request.input_currency_value,
                decimal=input_currency.decimal,
            )
            output_currency = self.request.output_method.currency
            output_currency_id_str = output_currency.id_str.upper()
            output_value = value_to_float(
                value=self.request.output_currency_value,
                decimal=output_currency.decimal,
            )
        value_str = (
            f'{value_to_str(value=input_value)} {input_currency_id_str}'
            f' -> '
            f'{value_to_str(value=output_value)} {output_currency_id_str}'
        )
        rate_str = value_to_str(value=get_fix_rate(rate=rate))
        if self.request.name:
            value_str = f'{self.request.name} ({value_str})'
        state_row = await self.client.session.gtv(key=f'request_state_{self.request.state}')
        rate_controls = [
            Text(
                value=rate_str,
                size=settings.get_font_size(multiple=1.5),
                font_family=Fonts.SEMIBOLD,
                color=colors.ON_PRIMARY_CONTAINER,
            ),
        ]
        if self.request.state not in [RequestStates.CANCELED, RequestStates.COMPLETED]:
            rate_controls += [
                DynamicTimer(
                    seconds=self.request.rate_fixed_delta,
                    font_family=Fonts.SEMIBOLD,
                    color=colors.ON_PRIMARY_CONTAINER,
                ),
            ]
        info_card_controls = [
            Row(
                controls=[
                    Text(
                        value=value_str,
                        size=settings.get_font_size(multiple=3),
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
                        on_click=self.request_edit_name_open,
                    ),
                ],
                wrap=True,
            ),
            Divider(color=colors.ON_PRIMARY_CONTAINER),
            Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_id'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=f'{self.request.id:08}',
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
                        value=state_row,
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
                        value=await self.client.session.gtv(key='rate'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Row(
                        controls=rate_controls,
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
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                        Text(
                            value=await self.client.session.gtv(key=self.request.input_method.name_text),
                            size=settings.get_font_size(multiple=1.5),
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
                            size=settings.get_font_size(multiple=1.5),
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                        Text(
                            value=await self.client.session.gtv(key=self.request.output_method.name_text),
                            size=settings.get_font_size(multiple=1.5),
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
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_PRIMARY_CONTAINER,
                    ),
                    Text(
                        value=self.request.date.strftime('%Y-%m-%d, %H:%M:%S'),
                        size=settings.get_font_size(multiple=1.5),
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

    async def update_confirmation_timer(self, update: bool = True):
        self.confirmation_timer = DynamicTimer(
            seconds=self.request.confirmation_delta,
        )
        if update:
            await self.confirmation_timer.update_async()

    async def update_confirmation_true_button(self, update: bool = True) -> None:
        self.confirmation_true_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_confirm_true'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.BOLD,
                    ),
                    self.confirmation_timer,
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.GREEN,
            on_click=partial(self.confirmation_answer, True),
            expand=1,
        )
        if update:
            await self.confirmation_true_button.update_async()

    async def update_confirmation_false_button(self, update: bool = True) -> None:
        self.confirmation_false_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_confirm_false'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.BOLD,
                    ),
                    self.confirmation_timer,
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            bgcolor=colors.RED,
            on_click=partial(self.confirmation_answer, False),
            expand=1,
        )
        if update:
            await self.confirmation_false_button.update_async()

    async def update_cancel_button(self, update: bool = True) -> None:
        self.cancellation_button = StandardButton(
            content=Row(
                controls=[
                    Text(
                        value=await self.client.session.gtv(key='request_cancellation_title'),
                        size=settings.get_font_size(multiple=1.5),
                        font_family=Fonts.BOLD,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            on_click=self.cancellation,
            expand=1,
        )
        if update:
            await self.cancellation_button.update_async()

    """
    ORDERS SEND
    """

    async def get_orders_cards(self, type_: str):
        cards: list = []
        for order in self.orders:
            if order.type != type_:
                continue
            currency = order.currency
            requisite_data_str = ', '.join([
                value_
                for key_, value_ in order.requisite_fields.items()
            ])
            state_str = await self.client.session.gtv(key=f'request_order_{order.type}_{order.state}')
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

    async def update_client_text(self, update: bool = True, _=None):
        self.client_text_column.controls = []
        input_currency_value = None
        if self.request.input_currency_value:
            input_currency_value = value_to_float(
                value=self.request.input_currency_value,
                decimal=self.request.input_method.currency.decimal,
            )
        input_rate = value_to_float(value=self.request.input_rate, decimal=self.request.rate_decimal)
        input_value = value_to_float(value=self.request.input_value)
        output_value = value_to_float(value=self.request.output_value)
        output_rate = value_to_float(value=self.request.output_rate, decimal=self.request.rate_decimal)
        output_currency_value = None
        if self.request.output_currency_value:
            output_currency_value = value_to_float(
                value=self.request.output_currency_value,
                decimal=self.request.output_method.currency.decimal,
            )
        input_method, input_currency = None, None
        if self.request.input_method:
            input_method = await self.client.session.gtv(key=self.request.input_method.name_text)
            input_currency = self.request.input_method.currency.id_str.upper()
        output_method, output_currency = None, None
        if self.request.output_method:
            output_method = await self.client.session.gtv(key=self.request.output_method.name_text)
            output_currency = self.request.output_method.currency.id_str.upper()
        input_orders = []
        output_orders = []
        for i, order in enumerate(self.orders):
            if order.state == OrderStates.CANCELED:
                continue
            currency_value: str = value_to_str(
                value=value_to_float(value=order.currency_value, decimal=order.method.currency.decimal),
            )
            data = [
                ', '.join([f'{value}' for key, value in order.requisite_fields.items()]),
                ' '.join([currency_value, order.method.currency.id_str.upper()])
            ]
            if order.type == OrderTypes.INPUT:
                input_orders += [' -> '.join(data)]
            elif order.type == OrderTypes.OUTPUT:
                output_orders += [' -> '.join(data)]
        if len(input_orders) > 1:
            for i, input_order in enumerate(input_orders):
                input_orders[i] = f'{i + 1}. {input_order}'
        if len(output_orders) > 1:
            for i, output_order in enumerate(output_orders):
                output_orders[i] = f'{i + 1}. {output_order}'
        if self.account_client_text:
            self.client_text_column.controls = [
                TextField(
                    label=await self.client.session.gtv(key='request_get_client_text'),
                    multiline=True,
                    value=value_replace(
                        self.account_client_text.value,
                        name=self.request.name,
                        type=self.request.type,
                        state=self.request.state,
                        commission=self.request.commission,
                        rate=self.request.rate,
                        input_currency_value=input_currency_value,
                        input_rate=input_rate,
                        input_value=input_value,
                        output_value=output_value,
                        output_rate=output_rate,
                        output_currency_value=output_currency_value,
                        date=self.request.date,
                        confirmation_delta=self.request.confirmation_delta,
                        rate_fixed_delta=self.request.rate_fixed_delta,
                        input_method=input_method,
                        input_currency=input_currency,
                        input_orders='\n'.join(input_orders),
                        output_method=output_method,
                        output_currency=output_currency,
                        output_orders='\n'.join(output_orders),
                    ),
                ),
            ]
        if update:
            await self.client_text_column.update_async()

    async def construct(self):
        controls, buttons = [], []
        await self.set_type(loading=True)
        self.request = await self.client.session.api.client.requests.get(id_=self.request_id)
        self.orders = await self.client.session.api.client.orders.list_get.by_request(request_id=self.request_id)
        self.account_client_text = await self.client.session.api.client.accounts.clients_texts.get(
            key=f'request_{self.request.type}_{self.request.state}',
        )
        await self.set_type(loading=False)
        await self.update_info_card(update=False)
        controls += [
            self.info_card,
        ]
        if self.confirmation_timer:
            self.confirmation_timer.running = False
        if self.request.state == 'confirmation':
            await self.update_confirmation_timer(update=False)
            await self.update_confirmation_false_button(update=False)
            await self.update_confirmation_true_button(update=False)
            buttons += [
                Row(
                    controls=[
                        self.confirmation_false_button,
                        self.confirmation_true_button,
                    ],
                ),
            ]
        elif self.request.state in [RequestStates.COMPLETED, RequestStates.CANCELED]:
            await self.update_orders_row(update=False)
            controls += [
                self.orders_row,
            ]
        else:
            await self.update_orders_row(update=False)
            controls += [
                self.orders_row,
            ]
            await self.update_cancel_button(update=False)
            buttons += [
                Row(
                    controls=[
                        self.cancellation_button,
                    ],
                ),
            ]
        self.client_text_column = Column()
        await self.update_client_text(update=False)
        controls += [
            self.client_text_column,
        ]
        title_str = await self.client.session.gtv(key='request_get_title')
        self.controls = await self.get_controls(
            title=f'{title_str} #{self.request.id:08}',
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

    async def request_edit_name_close(self, _):
        self.dialog.open = False
        await self.update_async()

    async def request_edit_name_open(self, _):
        self.request_edit_name_model = RequestUpdateNameModel(
            session=self.client.session,
            update_async=self.update_async,
            request_id=self.request.id,
            request_name=self.request.get('name'),
            after_close=self.edit_name_after,
            close_func=self.request_edit_name_close,
        )
        await self.request_edit_name_model.construct()
        self.dialog.content = Container(
            content=Column(
                controls=self.request_edit_name_model.controls,
                scroll=ScrollMode.AUTO,
            ),
        )
        self.dialog.actions = self.request_edit_name_model.buttons
        self.dialog.open = True
        await self.update_async()

    async def edit_name_after(self):
        self.dialog.open = False
        await self.dialog.update_async()

    async def order_view(self, order_id: int, _):
        await self.client.change_view(view=RequestOrderView(order_id=order_id))

    async def confirmation_answer(self, answer: bool, _):
        try:
            await self.client.session.api.client.requests.updates.confirmation(id_=self.request_id, answer=answer)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def cancellation(self, _):
        try:
            await self.client.session.api.client.requests.updates.cancellation(id_=self.request_id)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            return await self.client.session.error(exception=exception)
