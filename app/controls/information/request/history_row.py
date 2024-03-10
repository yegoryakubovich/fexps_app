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
from config import settings


class RequestInfo:
    type_: str
    state: str
    value: str
    color: str
    date: str

    def __init__(self, type_: str, state: str, value: str, color: str, date: str) -> None:
        self.type_ = type_
        self.state = state
        self.value = value
        self.color = color
        self.date = date


class RequestHistoryChip(Chip):
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


class RequestTransactionCard(FletCard):
    def __init__(self, request: RequestInfo, **kwargs):
        super().__init__(**kwargs)
        self.content = Container(
            content=Column(controls=[
                FletRow(
                    controls=[
                        FletColumn(controls=[Text(
                            value=request.type_,
                            size=28,
                            font_family=Fonts.REGULAR,
                            color=colors.ON_BACKGROUND,
                        )]),
                        FletColumn(controls=[Text(
                            value=request.value,
                            size=32,
                            font_family=Fonts.REGULAR,
                            color=request.color,
                        )]),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                FletRow(
                    controls=[
                        FletColumn(
                            controls=[Text(
                                value=request.state,
                                size=16,
                                font_family=Fonts.REGULAR,
                                color=colors.ON_BACKGROUND,
                            )],
                        ),
                        FletColumn(controls=[Text(
                            value=request.date,
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


class RequestHistoryRow(FletRow):
    def __init__(
            self,
            title_text: str,
            filter_chips: list,
            requests_list: list[RequestInfo],
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.controls = [
            FletRow(controls=[Text(
                value=title_text,
                size=32,
                font_family=Fonts.BOLD,
                color=colors.ON_BACKGROUND,
            )]),
            *filter_chips,
            *[
                RequestTransactionCard(request=request)
                for request in requests_list
            ]
        ]
        self.wrap = True
