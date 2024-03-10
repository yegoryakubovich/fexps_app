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


from flet_core import Card as FletCard, Row as FletRow, Container, Column, colors, Row, \
    MainAxisAlignment
from flet_core.dropdown import Option

from app.controls.information import Text
from app.controls.input import Dropdown
from app.utils import Fonts
from config import settings


def find_option(options: list[Option], id_: int) -> Option:
    for option in options:
        if option.key == id_:
            return option
    return options[0]


class HomeBalanceCard(FletCard):
    def __init__(self, wallets: list, current_wallet, on_change):
        super().__init__()
        self.margin = 0
        self.width = 3000
        wallet_options = [Option(key=wallet.id, text=f'#{wallet.id} - {wallet.name}') for wallet in wallets]
        self.dd_wallets = Dropdown(
            value=find_option(options=wallet_options, id_=current_wallet.id).key,
            options=wallet_options,
            on_change=on_change,
            bgcolor=colors.BLACK,
            width=150,
        )
        self.content = Container(
            content=Row(
                controls=[
                    Column(
                        controls=[
                            Row(
                                controls=[Text(
                                    value=f'#{current_wallet.id} - {current_wallet.name}',
                                    size=24,
                                    font_family=Fonts.REGULAR,
                                    color=colors.GREY_400,
                                )],
                                alignment=MainAxisAlignment.CENTER,
                            ),
                            Row(
                                controls=[Text(
                                    value=f'${current_wallet.value / settings.default_decimal}',
                                    size=28,
                                    font_family=Fonts.REGULAR,
                                    color=colors.WHITE,
                                )],
                                alignment=MainAxisAlignment.CENTER,
                            ),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                        expand=True,
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            ),
            ink=True,
            padding=10,
            border_radius=10,
            margin=10,
        )
        if len(wallets) > 1:
            self.content.content.controls.append(self.dd_wallets)
        self.color = colors.BLUE_700


class HomeBalanceRow(FletRow):
    def __init__(self, wallets: list, current_wallet, on_change):
        super().__init__()
        self.controls = [
            HomeBalanceCard(
                wallets=wallets,
                current_wallet=current_wallet,
                on_change=on_change,
            ),
        ]
        self.wrap = True
        self.alignment = MainAxisAlignment.CENTER
