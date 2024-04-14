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


from flet_core import Row, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AdminBaseView
from app.utils import Error
from fexps_api_client.utils import ApiException
from .get import CurrencyView


class CurrencyCreateView(AdminBaseView):
    route = '/admin/currency/create'
    tf_id_str: TextField
    tf_decimal: TextField
    tf_rate_decimal: TextField
    tf_div: TextField

    async def build(self):
        self.tf_id_str = TextField(
            label='id_str',
        )
        self.tf_decimal = TextField(
            label=await self.client.session.gtv(key='currency_decimal'),
            value='2',
        )
        self.tf_rate_decimal = TextField(
            label=await self.client.session.gtv(key='currency_rate_decimal'),
            value='2',
        )
        self.tf_div = TextField(
            label=await self.client.session.gtv(key='currency_div'),
            value='100',
        )
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_currency_create_view_title'),
            main_section_controls=[
                self.tf_id_str,
                self.tf_decimal,
                self.tf_rate_decimal,
                self.tf_div,
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='create'),
                                size=16,
                            ),
                            on_click=self.create_currency,
                            expand=True,
                        ),
                    ],
                ),
            ],
        )

    async def create_currency(self, _):
        await self.set_type(loading=True)
        for field, min_len, max_len in [(self.tf_id_str, 2, 32)]:
            if not await Error.check_field(self, field, min_len=min_len, max_len=max_len):
                await self.set_type(loading=False)
                return
        for field in [self.tf_decimal, self.tf_rate_decimal, self.tf_div]:
            if not await Error.check_field(self, field, check_int=True):
                await self.set_type(loading=False)
                return
        try:
            id_str = await self.client.session.api.admin.currencies.create(
                id_str=self.tf_id_str.value,
                decimal=int(self.tf_decimal.value),
                rate_decimal=int(self.tf_rate_decimal.value),
                div=int(self.tf_div.value),
            )
            await self.set_type(loading=False)
            await self.client.change_view(view=CurrencyView(currency_id_str=id_str), delete_current=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
