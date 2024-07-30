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


from flet_core import Column, Container, Row, alignment, ScrollMode

from app.controls.button import StandardButton
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Error
from app.utils.value import get_decimal_places, value_to_int
from fexps_api_client.utils import ApiException


class TransferCreateView(ClientBaseView):
    route = '/client/transfer/create'
    wallet_to_id_tf: TextField
    value_tf: TextField

    async def construct(self):
        # self.client.session.account
        self.wallet_to_id_tf = TextField(
            label=await self.client.session.gtv(key='send_money_wallet_to_id'),
        )
        self.value_tf = TextField(
            label=await self.client.session.gtv(key='send_money_value'),
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='send_money'),
            with_expand=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=[
                            self.wallet_to_id_tf,
                            self.value_tf,
                        ],
                        scroll=ScrollMode.AUTO,
                    ),
                    expand=True
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                text=await self.client.session.gtv(key='send_money'),
                                on_click=self.send,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center
                )
            ],
        )

    async def go_back(self, _):
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)

    async def send(self, _):
        if not await Error.check_field(self, self.wallet_to_id_tf, check_int=True):
            return
        if not await Error.check_field(self, self.value_tf, check_float=True):
            return
        if get_decimal_places(float(self.value_tf.value)) > 2:
            self.value_tf.error_text = await self.client.session.gtv(key='payment_too_many_decimal_places')
            await self.update_async()
            return
        try:
            await self.client.session.api.client.transfers.create(
                wallet_from_id=self.client.session.current_wallet['id'],
                wallet_to_id=int(self.wallet_to_id_tf.value),
                value=value_to_int(value=self.value_tf.value),
            )
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            return await self.client.session.error(exception=exception)
