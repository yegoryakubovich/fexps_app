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

from flet_core import Column, colors, SnackBar, Control, FilledButton, ScrollMode, Row, MainAxisAlignment

from app.controls.information import Text, Card
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from app.views.client.requests.orders import OrderView
from config import settings


class RequestView(AdminBaseView):
    route = '/client/request/get'
    request = dict
    orders: list
    snack_bar: SnackBar
    custom_info: list
    custom_controls: list[Control]
    orders_list: Row

    def __init__(self, request_id: int):
        super().__init__()
        self.request_id = request_id

    async def get_order_row(self):
        cards = []
        for order in self.orders:
            currency = await self.client.session.api.client.currencies.get(id_str=order.currency)
            currency_value = order["currency_value"] / (10 ** currency['decimal'])
            value = order["value"] / (10 ** settings.default_decimal)
            cards.append(
                Card(
                    controls=[
                        Row(
                            controls=[
                                Text(
                                    value=f'#{order["id"]}',
                                    size=18,
                                    font_family=Fonts.SEMIBOLD,
                                    color=colors.ON_PRIMARY,
                                ),
                                Text(
                                    value=f'{currency_value}({currency.id_str.upper()})->{value}',
                                    size=18,
                                    font_family=Fonts.SEMIBOLD,
                                    color=colors.GREY,
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        Row(
                            controls=[
                                Text(
                                    value=order['type'],
                                    size=18,
                                    font_family=Fonts.SEMIBOLD,
                                    color=colors.ON_PRIMARY,
                                ),
                                Text(
                                    value=order['state'],
                                    size=18,
                                    font_family=Fonts.SEMIBOLD,
                                    color=colors.ON_PRIMARY,
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    on_click=partial(self.order_view, order['id']),
                )
            )
        return Row(
            controls=[
                Row(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key='orders'),
                            size=32,
                            font_family=Fonts.BOLD,
                            color=colors.ON_BACKGROUND,
                        ),
                    ],
                ),
                *cards,
            ],
            wrap=True,
        )

    async def build(self):
        await self.set_type(loading=True)
        self.request = await self.client.session.api.client.request.get(id_=self.request_id)
        self.orders = await self.client.session.api.client.orders.list_get.by_request(request_id=self.request_id)
        self.custom_info = await self.get_info(request=self.request)
        self.custom_controls = await self._get_controls(request=self.request)
        await self.set_type(loading=False)
        self.snack_bar = SnackBar(content=Text(value=await self.client.session.gtv(key='successful')))
        self.scroll = ScrollMode.AUTO
        self.orders_list = await self.get_order_row()
        self.controls = await self.get_controls(
            title=f'#{self.request.id}',
            main_section_controls=[
                Column(
                    controls=[
                        Text(
                            value='\n'.join(self.custom_info),
                            size=24,
                            font_family=Fonts.MEDIUM,
                            color=colors.ON_BACKGROUND,
                        ),
                        *self.custom_controls,
                        self.orders_list,
                    ],
                ),
            ],
        )

    async def order_view(self, order_id: int, _):
        await self.client.change_view(view=OrderView(order_id=order_id))

    async def get_info(self, request) -> list[str]:
        wallet = await self.client.session.api.client.wallets.get(id_=request.wallet)
        request_type_name: str = await self.client.session.gtv(key=f'request_type_{request.type}')
        request_state_name: str = await self.client.session.gtv(key=f'request_state_{request.state}')
        rate_confirmed_name: str = await self.client.session.gtv(key=f'{request.rate_confirmed}'.lower())
        result = [
            f'{await self.client.session.gtv(key="wallet")}: #{wallet.id} {wallet.name}',
            f'{await self.client.session.gtv(key="type")}: {request_type_name}',
            f'{await self.client.session.gtv(key="state")}: {request_state_name}',
            f'{await self.client.session.gtv(key="rate_confirmed")}: {rate_confirmed_name}',
        ]
        if request.type in ['input', 'all']:
            input_method = await self.client.session.api.client.methods.get(id_=request.input_method)
            input_currency = await self.client.session.api.client.currencies.get(id_str=input_method.currency)
            if request.rate_confirmed and request.input_currency_value_raw and request.input_value_raw:
                input_currency_value = request.input_currency_value_raw / (10 ** input_currency.decimal)
                input_value = request.input_value_raw / (10 ** input_currency.decimal)
            elif not request.rate_confirmed and request.input_currency_value and request.input_value:
                input_currency_value = request.input_currency_value / (10 ** input_currency.decimal)
                input_value = request.input_value / (10 ** input_currency.decimal)
            else:
                input_currency_value = None
                input_value = None
            result += [
                f'{await self.client.session.gtv(key="input_currency")}: {input_currency.id_str.upper()}',
                f'{await self.client.session.gtv(key="input_method")}: '
                f'#{input_method.id} {await self.client.session.gtv(key=input_method.name_text)}',
                f'{await self.client.session.gtv(key="input_currency_value")}: {input_currency_value}',
                f'{await self.client.session.gtv(key="input_value")}: {input_value}',
            ]
        if request.type in ['output', 'all']:
            output_requisite_data = await self.client.session.api.client.requisite_data.get(
                id_=request.output_requisite_data,
            )
            output_currency = await self.client.session.api.client.currencies.get(id_str=output_requisite_data.currency)
            if request.rate_confirmed and request.output_currency_value_raw and request.output_value_raw:
                output_currency_value = request.output_currency_value_raw / (10 ** output_currency.decimal)
                output_value = request.output_value_raw / (10 ** output_currency.decimal)
            elif not request.rate_confirmed and request.output_currency_value and request.output_value:
                output_currency_value = request.output_currency_value / (10 ** output_currency.decimal)
                output_value = request.output_value / (10 ** output_currency.decimal)
            else:
                output_currency_value = 0
                output_value = 0
            result += [
                f'{await self.client.session.gtv(key="output_currency")}: {output_currency.id_str.upper()}',
                f'{await self.client.session.gtv(key="output_requisite_data")}: '
                f'#{output_requisite_data.id} {output_requisite_data.name}',
                f'{await self.client.session.gtv(key="output_currency_value")}: {output_currency_value}',
                f'{await self.client.session.gtv(key="output_value")}: {output_value}',
            ]
        rate = request.rate / (10 ** request.rate_decimal) if request.rate else None
        result += [
            f'{await self.client.session.gtv(key="rate")}: {rate}',
        ]
        return result

    async def _get_controls_input_fields(self, order):
        result = []
        if order.requisite_fields:
            requisite_data = [
                await self.client.session.gtv(key="requisite_data"),
            ]
            for key, value in order.requisite_fields.items():
                logging.critical(key)
                logging.critical(value)

        return result

    async def _get_controls(self, request) -> list[Control]:
        result = []
        state_info = Text(value=None, size=24, font_family=Fonts.MEDIUM, color=colors.ON_BACKGROUND)
        buttons = []
        if request.state == 'loading':
            state_info.value = await self.client.session.gtv(key='request_loading_info')
        elif request.state == 'waiting':
            state_info.value = await self.client.session.gtv(key='request_waiting_info')
            buttons.append(FilledButton(
                content=Text(value=await self.client.session.gtv(key='confirm')),
                on_click=self.waiting_confirm,
            ))
        elif request.state == 'input_reservation':
            state_info.value = await self.client.session.gtv(key='request_input_reservation_info')
        elif request.state == 'input':
            state_info.value = await self.client.session.gtv(key='request_input_info')
        elif request.state == 'output_reservation':
            state_info.value = await self.client.session.gtv(key='request_output_reservation_info')
        elif request.state == 'output':
            state_info.value = await self.client.session.gtv(key='request_output_info')
        elif request.state == 'completed':
            state_info.value = await self.client.session.gtv(key='request_completed_info')
        elif request.state == 'canceled':
            state_info.value = await self.client.session.gtv(key='request_canceled_info')
        result.append(state_info)
        if buttons:
            result += buttons
        return result

    async def waiting_confirm(self, _):
        await self.client.session.api.client.request.update_confirmation(id_=self.request_id)
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
