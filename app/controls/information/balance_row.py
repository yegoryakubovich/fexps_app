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


from flet_core import Card as FletCard, Container, Column, colors, Row, MainAxisAlignment
from flet_core import Row as FletRow

from app.controls.information import Text
from app.utils import Fonts


class BalanceCard(FletCard):
    def __init__(self, wallet_name: str, wallet_balance: int, **kwargs):
        super().__init__(**kwargs)
        self.margin = 0
        self.width = 3000
        self.content = Container(
            content=Column(
                controls=[
                    Row(
                        controls=[Text(
                            value=wallet_name,
                            size=24,
                            font_family=Fonts.REGULAR,
                            color=colors.GREY_400,
                        )],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    Row(
                        controls=[Text(
                            value=f'${wallet_balance}',
                            size=28,
                            font_family=Fonts.REGULAR,
                            color=colors.WHITE,
                        )],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                ],
            ),
            ink=True,
            padding=10,
            border_radius=10,
            margin=10,
        )
        self.color = colors.BLUE_700


class BalanceRow(FletRow):
    def __init__(self, wallet_name: str, wallet_value: int, **kwargs):
        super().__init__(**kwargs)
        self.controls = [
            BalanceCard(
                wallet_name=wallet_name,
                wallet_balance=wallet_value,
            ),
        ]
        self.wrap = True
        self.alignment = MainAxisAlignment.CENTER
