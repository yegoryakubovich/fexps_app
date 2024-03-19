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


from flet_core import Column, Container, ScrollMode, padding, colors, KeyboardType, Row

from app.controls.button import FilledButton, StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from app.utils import Fonts
from app.utils.value import get_decimal_places
from config import settings
from fexps_api_client.utils import ApiException


class SendMoneyView(ClientBaseView):
    route = '/client/actions/money/send'
    wallet_to_id_tf: TextField
    value_tf: TextField
    controls_container: Container

    async def build(self):
        # self.client.session.account
        self.wallet_to_id_tf = TextField(
            label=await self.client.session.gtv(key='actions_send_wallet_to_id'),
            keyboard_type=KeyboardType.NUMBER,
        )
        self.value_tf = TextField(
            label=await self.client.session.gtv(key='actions_send_value'),
            keyboard_type=KeyboardType.NUMBER,
        )
        self.controls_container = Container(
            content=Column(
                controls=[
                    self.wallet_to_id_tf,
                    self.value_tf,
                    Row(
                        controls=[
                            StandardButton(
                                text=await self.client.session.gtv(key='send_money'),
                                on_click=self.switch_tf,
                                expand=True,
                            ),
                        ],
                    ),
                ],
                spacing=10,
            ),
            padding=padding.only(bottom=15),
        )
        controls = [
            self.controls_container
        ]
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='send_money'),
            main_section_controls=controls,
        )

    async def go_back(self, _):
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)

    async def switch_tf(self, _):
        self.wallet_to_id_tf.error_text = None
        self.value_tf.error_text = None
        if get_decimal_places(float(self.value_tf.value)) > 2:
            self.value_tf.error_text = await self.client.session.gtv(key='payment_too_many_decimal_places')
            await self.update_async()
            return
        try:
            await self.client.session.api.client.transfers.create(
                wallet_from_id=self.client.session.current_wallet.id,
                wallet_to_id=int(self.wallet_to_id_tf.value),
                value=int(float(self.value_tf.value) * settings.default_decimal),
            )
        except ApiException as e:
            if e.code in [1000, ]:
                self.wallet_to_id_tf.error_text = e.message
            elif e.code in [6002, ]:
                self.value_tf.error_text = e.message
            else:
                self.value_tf.error_text = f'{e.code} - {e.message}'
            await self.update_async()
            return
        self.controls_container = Container(
            content=Column(
                [
                    Text(
                        value=await self.client.session.gtv(key='payment_success'),
                        size=15,
                        font_family=Fonts.SEMIBOLD,
                        color=colors.ON_BACKGROUND,
                    ),
                    FilledButton(
                        text=await self.client.session.gtv(key='go_back'),
                        on_click=self.go_back,
                    )
                ]
            )
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='payment'),
            main_section_controls=[self.controls_container],
        )
        await self.update_async()
