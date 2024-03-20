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

from flet_core import Column, Container, padding, colors, Row

from app.controls.button import StandardButton
from app.controls.input import TextField
from app.controls.layout import ClientBaseView
from fexps_api_client.utils import ApiException


class WalletCreateView(ClientBaseView):
    route = '/client/wallets/create'
    tf_name: TextField

    async def build(self):
        self.tf_name = TextField(
            label=await self.client.session.gtv(key='wallet_name'),
            value='Default',
        )
        controls = [
            Container(
                content=Column(
                    controls=[
                        self.tf_name,
                        Row(
                            controls=[
                                StandardButton(
                                    text=await self.client.session.gtv(key='create'),
                                    on_click=self.create,
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                ),
                padding=padding.only(bottom=15),
            )
        ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='wallet_create'),
            main_section_controls=controls,
        )

    async def go_back(self, _):
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)

    async def create(self, _):
        try:
            await self.client.session.api.client.wallets.create(name=self.tf_name.value)
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            return await self.client.session.error(exception=exception)
