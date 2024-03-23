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

from flet_core import Row

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AdminBaseView


class CurrencyView(AdminBaseView):
    route = '/admin/currency/get'
    currency = dict
    tf_decimal: TextField
    tf_rate_decimal: TextField
    tf_div: TextField

    def __init__(self, currency_id_str):
        super().__init__()
        self.currency_id_str = currency_id_str

    async def build(self):
        await self.set_type(loading=True)
        self.currency = await self.client.session.api.client.currencies.get(
            id_str=self.currency_id_str,
        )
        await self.set_type(loading=False)
        self.tf_decimal = TextField(
            label=await self.client.session.gtv(key='decimal'),
            value=self.currency['decimal'],
        )
        self.tf_rate_decimal = TextField(
            label=await self.client.session.gtv(key='rate_decimal'),
            value=self.currency['rate_decimal'],
        )
        self.tf_div = TextField(
            label=await self.client.session.gtv(key='div'),
            value=self.currency['div'],
        )

        self.controls = await self.get_controls(
            title=self.currency['id_str'].upper(),
            main_section_controls=[
                self.tf_decimal,
                self.tf_rate_decimal,
                self.tf_div,
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='save'),
                            ),
                            on_click=self.update_currency,
                            expand=True,
                        ),
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='delete'),
                            ),
                            on_click=self.delete_currency,
                            expand=True,
                        ),
                    ]
                ),
            ],
        )

    async def update_currency(self, _):
        await self.client.session.api.admin.currencies.update(
            id_str=self.currency_id_str,
            decimal=self.tf_decimal.value,
            rate_decimal=self.tf_rate_decimal.value,
            div=self.tf_div.value,
        )
        await self.client.change_view(go_back=True, with_restart=True)

    async def delete_currency(self, _):
        await self.client.session.api.admin.currencies.delete(
            id_str=self.currency_id_str,
        )
        await self.client.change_view(go_back=True, with_restart=True)
