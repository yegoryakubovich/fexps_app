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

from flet_core import Column, Container, padding, colors, Row, MainAxisAlignment, alignment

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import ClientBaseView
from app.utils import Fonts
from config import settings


class WalletSelectView(ClientBaseView):
    route = '/client/wallet/select'
    wallets: list
    wallets_column: Column
    selected_wallet_id: int

    async def get_wallet_list(self):
        wallets_list = []
        for wallet in self.wallets:
            value = f'{wallet.value / 10 ** settings.default_decimal}'.replace('.', ',')
            bgcolor = colors.GREY_400
            if self.selected_wallet_id == wallet.id:
                bgcolor = colors.SECONDARY
            wallets_list.append(Row(controls=[StandardButton(
                content=Row(
                    controls=[
                        Text(
                            value=f'{wallet.name}',
                            size=28,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_BACKGROUND,
                        ),
                        Text(
                            value=f'{value}',
                            size=28,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_BACKGROUND,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=bgcolor,
                vertical=100,
                on_click=partial(self.select_wallet, wallet.id),
                expand=True,
            )]))
        return wallets_list

    async def build(self):
        # self.client.session.account
        await self.set_type(loading=True)
        self.wallets = await self.client.session.api.client.wallets.get_list()
        await self.set_type(loading=False)
        self.selected_wallet_id = self.client.session.current_wallet.id
        self.wallets_column = Column(controls=await self.get_wallet_list())

        controls = [
            self.wallets_column,
            Container(
                content=Column(
                    controls=[
                        Row(
                            controls=[
                                StandardButton(
                                    text=await self.client.session.gtv(key='edit_name'),
                                    on_click=None,
                                    expand=True,
                                    bgcolor=colors.GREY_400,
                                ),
                                StandardButton(
                                    text=await self.client.session.gtv(key='permissions'),
                                    on_click=None,
                                    expand=True,
                                    bgcolor=colors.GREY_400,
                                ),
                            ],
                            spacing=16,
                        ),
                        Row(
                            controls=[
                                StandardButton(
                                    text=await self.client.session.gtv(key='create_new_wallet'),
                                    on_click=None,
                                    expand=True,
                                    bgcolor=colors.GREY_400,
                                ),
                            ],
                        ),
                        Row(
                            controls=[
                                StandardButton(
                                    text=await self.client.session.gtv(key='Select'),
                                    on_click=self.switch_wallet,
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                ),
                padding=padding.only(bottom=15),
                alignment=alignment.bottom_center,
                expand=True,

            )
        ]
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='wallets'),
            with_expand=True,
            main_section_controls=controls,
        )

    async def go_back(self, _):
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)

    async def select_wallet(self, wallet_id: int, _):
        self.selected_wallet_id = wallet_id
        self.wallets_column.controls = await self.get_wallet_list()
        await self.update_async()

    async def switch_wallet(self, _):
        for wallet in self.wallets:
            if self.selected_wallet_id == wallet.id:
                self.client.session.current_wallet = wallet
                await self.client.session.set_cs(key='current_wallet', value=self.client.session.current_wallet)
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)