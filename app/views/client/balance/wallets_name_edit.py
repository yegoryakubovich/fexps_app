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


class WalletNameEditView(ClientBaseView):
    route = '/client/wallets/name/edit'
    wallet_id: int
    tf_new_name: TextField

    def __init__(self, wallet_id: int, **kwargs):
        super().__init__(**kwargs)
        self.wallet_id = wallet_id

    async def build(self):
        await self.set_type(loading=True)
        wallet = await self.client.session.api.client.wallets.get(id_=self.wallet_id)
        await self.set_type(loading=False)
        self.tf_new_name = TextField(
            label=await self.client.session.gtv(key='wallet_new_name'),
            value=wallet.name,
        )
        controls = [
            Container(
                content=Column(
                    controls=[
                        self.tf_new_name,
                        Row(
                            controls=[
                                StandardButton(
                                    text=await self.client.session.gtv(key='edit_name'),
                                    on_click=self.edit_name,
                                    expand=True,
                                    bgcolor=colors.SECONDARY,
                                ),
                            ],
                        ),
                    ],
                ),
                padding=padding.only(bottom=15),
            )
        ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='edit_name'),
            main_section_controls=controls,
        )

    async def go_back(self, _):
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)

    async def edit_name(self, _):
        await self.client.session.api.client.wallets.update(
            id_=self.wallet_id,
            name=self.tf_new_name.value,
        )
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
