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


from flet_core import Card as FletCard, Container, Column, colors, MainAxisAlignment, Chip
from flet_core import Column as FletColumn
from flet_core import Row as FletRow

from app.controls.information import Text
from app.utils import Fonts
from app.utils.value import get_history_value_cleaned, get_history_color


class HistoryChip(Chip):
    def __init__(self, name: str, key: str, on_select, **kwargs):
        self.label = Text(
            value=name,
            size=16,
            font_family=Fonts.BOLD,
            color=colors.ON_BACKGROUND,
        )
        super().__init__(label=self.label, **kwargs)
        self.bgcolor = colors.GREEN
        self.key = key
        self.on_select = on_select


class TransactionCard(FletCard):
    def __init__(self, transfer, **kwargs):
        super().__init__(**kwargs)
        self.content = Container(
            content=Column(controls=[
                FletRow(
                    controls=[
                        FletColumn(controls=[Text(
                            value='Transfer',
                            size=28,
                            font_family=Fonts.REGULAR,
                            color=colors.ON_BACKGROUND,
                        )]),
                        FletColumn(controls=[Text(
                            value=get_history_value_cleaned(value=transfer.value),
                            size=32,
                            font_family=Fonts.REGULAR,
                            color=get_history_color(value=transfer.value),
                        )]),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                FletRow(
                    controls=[
                        FletColumn(
                            controls=[Text(
                                value=f'from wallet.{transfer.wallet_from} to wallet.{transfer.wallet_to}',
                                size=16,
                                font_family=Fonts.REGULAR,
                                color=colors.ON_BACKGROUND,
                            )],
                        ),
                        FletColumn(controls=[Text(
                            value=transfer.date,
                            size=16,
                            font_family=Fonts.REGULAR,
                            color=colors.ON_BACKGROUND,
                        )]),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
            ]),
            ink=True,
            padding=10,
            border_radius=10,
            margin=10,
        )
        self.color = colors.GREY_800


class HistoryRow(FletRow):
    def __init__(self, title_text: str, filter_chips: list, transfers: list, **kwargs):
        super().__init__(**kwargs)
        self.controls = [
            FletRow(
                controls=[
                    Text(
                        value=title_text,
                        size=32,
                        font_family=Fonts.BOLD,
                        color=colors.ON_BACKGROUND,
                    )
                ]
            ),
            *filter_chips,
            *[TransactionCard(transfer=transfer) for transfer in transfers]
        ]
        self.wrap = True
