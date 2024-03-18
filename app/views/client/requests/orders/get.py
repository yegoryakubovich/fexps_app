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

from flet_core import SnackBar, Control, Column, colors, FilledButton

from app.controls.information import Text
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from config import settings


class OrderView(AdminBaseView):
    route = '/client/request/order/get'
    order = dict
    snack_bar: SnackBar
    custom_info: list
    custom_controls: list[Control]

    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id

    async def build(self):
        await self.set_type(loading=True)
        self.order = await self.client.session.api.client.orders.get(id_=self.order_id)
        self.custom_info = await self.get_info(order=self.order)
        self.custom_controls = await self._get_controls(order=self.order)
        await self.set_type(loading=False)
        logging.critical(self.order)
        self.controls = await self.get_controls(
            title=f'#{self.order.id}',
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
                    ],
                ),
            ],
        )

    async def get_info(self, order):
        order_type_name: str = await self.client.session.gtv(key=f'order_type_{order.type}')
        order_state_name: str = await self.client.session.gtv(key=f'order_state_{order.state}')
        currency = await self.client.session.api.client.currencies.get(id_str=order.currency)
        currency_value = order.currency_value / (10 ** currency.decimal)
        rate = order.rate / (10 ** currency.rate_decimal)
        value = order.value / (10 ** settings.default_decimal)
        result = [
            f'{await self.client.session.gtv(key="type")}: {order_type_name}',
            f'{await self.client.session.gtv(key="state")}: {order_state_name}',
            f'{await self.client.session.gtv(key="request")}: #{order.request}',
            f'{await self.client.session.gtv(key="requisite")}: #{order.requisite}',
            f'{await self.client.session.gtv(key="currency")}: {currency.id_str.upper()}',
            f'{await self.client.session.gtv(key="currency_value")}: {currency_value}',
            f'{await self.client.session.gtv(key="value")}: {value}',
            f'{await self.client.session.gtv(key="rate")}: {rate}',
        ]
        if order.state == 'canceled' and order.canceled_reason:
            canceled_reason_name: str = await self.client.session.gtv(key=f'canceled_reason_{order.canceled_reason}')
            result += [
                f'{await self.client.session.gtv(key="canceled_reason")}: {canceled_reason_name}',
            ]
        return result

    async def _get_controls(self, order) -> list[Control]:
        requisite = await self.client.session.api.client.requisite.get(id_=order.requisite)
        logging.critical(requisite)
        state_info = Text(value=None, size=24, font_family=Fonts.MEDIUM, color=colors.ON_BACKGROUND)
        controls, buttons = [], []
        if order.state == 'waiting':
            state_info.value = await self.client.session.gtv(key='order_waiting_info')
        elif order.state == 'payment':
            if order.type == 'input':
                state_info.value = await self.client.session.gtv(key='order_input_payment_info')
                controls += [

                ]
                buttons.append(FilledButton(
                    content=Text(value=await self.client.session.gtv(key='payment_confirm')),
                    on_click=self.payment_confirm,
                ))
            elif order.type == 'output':
                state_info.value = await self.client.session.gtv(key='order_output_payment_info')
        elif order.state == 'confirmation':
            if order.type == 'input':
                state_info.value = await self.client.session.gtv(key='order_input_confirmation_info')
            elif order.type == 'output':
                state_info.value = await self.client.session.gtv(key='order_output_confirmation_info')
        elif order.state == 'completed':
            state_info.value = await self.client.session.gtv(key='order_completed_info')
        elif order.state == 'canceled':
            state_info.value = await self.client.session.gtv(key='order_canceled_info')
        return [state_info] + controls + buttons

    async def payment_confirm(self, _):
        pass
