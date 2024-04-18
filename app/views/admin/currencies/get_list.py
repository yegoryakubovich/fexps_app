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

from flet_core import Text, ScrollMode, colors

from app.controls.information.card import Card
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from app.views.admin.currencies.create import CurrencyCreateView
from app.views.admin.currencies.get import CurrencyView


class CurrencyListView(AdminBaseView):
    route = '/admin/currency/list/get'
    currencies: list[dict]

    async def construct(self):
        await self.set_type(loading=True)
        self.currencies = await self.client.session.api.client.currencies.get_list()
        await self.set_type(loading=False)

        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_currency_get_list_view_title'),
            on_create_click=self.currency_create,
            main_section_controls=[
                Card(
                    controls=[
                        Text(
                            value=currency['id_str'].upper(),
                            size=18,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                    on_click=partial(self.currency_view, currency['id_str']),
                    color=colors.PRIMARY_CONTAINER,
                )
                for currency in self.currencies
            ],
        )

    async def currency_create(self, _):
        await self.client.change_view(view=CurrencyCreateView())

    async def currency_view(self, currency_id_str: str, _):
        await self.client.change_view(view=CurrencyView(currency_id_str=currency_id_str))
