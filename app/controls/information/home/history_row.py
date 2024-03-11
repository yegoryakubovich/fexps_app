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
from app.controls.navigation.pagination import PaginationWidget
from app.utils import Fonts


class TransferInfo:
    type_: str
    description: str
    value: str
    color: str
    date: str

    def __init__(self, type_: str, description: str, value: str, color: str, date: str) -> None:
        self.type_ = type_
        self.description = description
        self.value = value
        self.color = color
        self.date = date


class HomeHistoryChip(Chip):
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


class HomeTransactionCard(FletCard):
    def __init__(self, transfer: TransferInfo, **kwargs):
        super().__init__(**kwargs)
        self.content = Container(
            content=Column(controls=[
                FletRow(
                    controls=[
                        FletColumn(controls=[Text(
                            value=transfer.type_,
                            size=28,
                            font_family=Fonts.REGULAR,
                            color=colors.ON_BACKGROUND,
                        )]),
                        FletColumn(controls=[Text(
                            value=transfer.value,
                            size=32,
                            font_family=Fonts.REGULAR,
                            color=transfer.color,
                        )]),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                FletRow(
                    controls=[
                        FletColumn(
                            controls=[Text(
                                value=transfer.description,
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


class HomeHistoryRow(FletRow):
    def __init__(
            self,
            title_text: str,
            filter_chips: list,
            transfer_list: list[TransferInfo],
            pagination: PaginationWidget = None,
            **kwargs,
    ):
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
            *[HomeTransactionCard(transfer=transfer) for transfer in transfer_list]
        ]
        if pagination:
            self.controls.append(pagination)
        self.wrap = True
