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

from flet_core import Column, Container, colors, Row, MainAxisAlignment, AlertDialog, TextField, alignment, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import ClientBaseView
from app.utils import Fonts
from config import settings
from fexps_api_client.utils import ApiException


class WalletSelectView(ClientBaseView):
    route = '/client/wallets/select'
    wallets: list
    wallet = dict
    wallets_column: Column
    selected_wallet_id: int
    dialog: AlertDialog
    tf_name: TextField

    def __init__(self, current_wallet_id, **kwargs):
        super().__init__(**kwargs)
        self.selected_wallet_id = current_wallet_id

    async def get_wallet_list(self):
        wallets_list = []
        for wallet in self.wallets:
            value = f'{wallet.value / 10 ** settings.default_decimal}'.replace('.', ',')
            bgcolor = colors.PRIMARY_CONTAINER
            color = colors.ON_PRIMARY_CONTAINER
            if self.selected_wallet_id == wallet.id:
                bgcolor = colors.PRIMARY
                color = colors.ON_PRIMARY
            wallets_list.append(
                Row(
                    controls=[
                        StandardButton(
                            content=Row(
                                controls=[
                                    Text(
                                        value=f'{wallet.name}',
                                        size=28,
                                        font_family=Fonts.SEMIBOLD,
                                        color=color,
                                    ),
                                    Text(
                                        value=f'{value}',
                                        size=28,
                                        font_family=Fonts.SEMIBOLD,
                                        color=color,
                                    ),
                                ],
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            bgcolor=bgcolor,
                            vertical=24,
                            on_click=partial(self.select_wallet, wallet.id),
                            expand=True,
                        ),
                    ],
                )
            )
        return wallets_list

    async def construct(self):
        self.dialog = AlertDialog()
        await self.set_type(loading=True)
        self.wallets = await self.client.session.api.client.wallets.get_list()
        self.wallet = await self.client.session.api.client.wallets.get(id_=self.client.session.current_wallet.id)
        self.wallets_column = Column(
            controls=await self.get_wallet_list(),
            scroll=ScrollMode.AUTO,
        )
        await self.set_type(loading=False)
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='wallet_select_title'),
            with_expand=True,
            main_section_controls=[
                self.dialog,
                Container(
                    content=self.wallets_column,
                    expand=True,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                text=await self.client.session.gtv(key='wallet_edit_name'),
                                on_click=self.dialog_edit_name_open,
                                color=colors.ON_PRIMARY_CONTAINER,
                                bgcolor=colors.PRIMARY_CONTAINER,
                                expand=True,
                            ),
                            StandardButton(
                                text=await self.client.session.gtv(key='wallet_permissions'),
                                on_click=None,
                                color=colors.ON_PRIMARY_CONTAINER,
                                bgcolor=colors.PRIMARY_CONTAINER,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                text=await self.client.session.gtv(key='wallet_select'),
                                on_click=self.switch_wallet,
                                expand=True,
                            ),
                        ],
                    ),
                ),
            ],
        )

    async def go_back(self, _):
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)

    async def select_wallet(self, wallet_id: int, _):
        self.selected_wallet_id = wallet_id
        await self.construct()
        await self.update_async()

    async def dialog_create_open(self, _):
        self.tf_name = TextField(
            label=await self.client.session.gtv(key='wallet_name'),
            value='Default',
        )
        self.dialog.content = Container(
            content=Column(
                controls=[
                    self.tf_name,
                ],
            ),
            height=100,
        )
        self.dialog.actions = [
            Row(
                controls=[
                    StandardButton(
                        text=await self.client.session.gtv(key='create'),
                        on_click=self.wallet_create,
                        expand=True,
                    ),
                ],
            ),
        ]
        self.dialog.modal = False
        self.dialog.open = True
        await self.update_async()

    async def wallet_create(self, _):
        try:
            await self.client.session.api.client.wallets.create(name=self.tf_name.value)
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def dialog_edit_name_open(self, _):
        self.tf_name = TextField(
            label=await self.client.session.gtv(key='wallet_name'),
            value=self.wallet.name,
        )
        self.dialog.content = Container(
            content=Column(
                controls=[
                    self.tf_name,
                ],
            ),
            height=100,
        )
        self.dialog.actions = [
            Row(
                controls=[
                    StandardButton(
                        text=await self.client.session.gtv(key='wallet_edit_name'),
                        on_click=partial(self.wallet_edit_name, self.selected_wallet_id),
                        expand=True,
                    ),
                ],
            ),
        ]
        self.dialog.modal = False
        self.dialog.open = True
        await self.update_async()

    async def wallet_edit_name(self, wallet_id: int, _):
        try:
            await self.client.session.api.client.wallets.update(
                id_=wallet_id,
                name=self.tf_name.value,
            )
            await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def switch_wallet(self, _):
        for wallet in self.wallets:
            if self.selected_wallet_id == wallet.id:
                self.client.session.current_wallet = wallet
                await self.client.session.set_cs(key='current_wallet', value=self.client.session.current_wallet)
        await self.client.change_view(go_back=True, delete_current=True, with_restart=True)
