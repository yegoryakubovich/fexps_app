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

from flet_core import Row, colors, MainAxisAlignment, Image, Column

from app.controls.button import StandardButton
from app.controls.information import SubTitle, Text
from app.controls.layout import ClientBaseView
from app.utils import Icons, Fonts, value_to_float
from app.views.client.requisites.orders.get import OrderView


class RequisiteView(ClientBaseView):
    route = '/client/requisite/get'
    requisite = dict
    orders = list[dict]

    def __init__(self, requisite_id: int):
        super().__init__()
        self.requisite_id = requisite_id

    """
    ORDERS
    """

    async def get_orders_cards(self):
        cards: list = []
        for order in self.orders:
            currency = await self.client.session.api.client.currencies.get(id_str=order.currency)
            state_str = await self.client.session.gtv(key=f'requisite_order_state_{order.state}')
            value = value_to_float(value=order.currency_value, decimal=currency.decimal)
            value_str = f'{value} {currency.id_str.upper()}'
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
                                                size=8,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=f'404 CARD NUMBER',
                                                size=28,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                    Row(
                                        controls=[
                                            Text(
                                                value=value_str,
                                                size=16,
                                                font_family=Fonts.SEMIBOLD,
                                                color=colors.ON_PRIMARY_CONTAINER,
                                            ),
                                        ],
                                    ),
                                ],
                                expand=True,
                            ),
                            Image(
                                src=Icons.OPEN,
                                height=32,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        spacing=2,
                    ),
                    on_click=partial(self.order_view, order.id),
                    bgcolor=colors.PRIMARY_CONTAINER,
                ),
            )
        return cards

    async def get_order_row(self) -> Row:
        return Row(
            controls=[
                SubTitle(value=await self.client.session.gtv(key='requisite_order_title')),
                *await self.get_orders_cards(),
            ],
            wrap=True,
        )

    async def build(self):
        await self.set_type(loading=True)
        self.requisite = await self.client.session.api.client.requisites.get(id_=self.requisite_id)
        self.orders = await self.client.session.api.client.orders.list_get.by_requisite(requisite_id=self.requisite_id)
        await self.set_type(loading=False)
        controls = [
            # await self.get_info_card(),
            await self.get_order_row(),
        ]
        self.controls = await self.get_controls(
            with_expand=True,
            title=f'{await self.client.session.gtv(key='requisite_get_title')} #{self.requisite.id:08}',
            main_section_controls=controls,
        )

    async def order_view(self, order_id: int, _):
        await self.client.change_view(view=OrderView(order_id=order_id))
