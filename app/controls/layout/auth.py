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
from typing import Any

from flet_core import Image, Container, padding, alignment, Column, ScrollMode, colors, Row, MainAxisAlignment, \
    CrossAxisAlignment
from flet_manager.utils import get_svg

from app.controls.information import Text
from app.controls.layout.view import View
from app.utils import Fonts, Icons


class AuthView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll = ScrollMode.AUTO

    async def go_back(self, _):
        await self.client.change_view(go_back=True)

    async def get_controls(
            self,
            controls: list,
            title: str = None,
            is_go_back: Any = False,
    ) -> list:

        body_controls = []

        back_control = Container(
            content=Image(
                src=Icons.BACK,
                height=20,
                color=colors.ON_BACKGROUND,
            ),
            ink=True,
            on_click=self.go_back,
        ) if is_go_back else None

        if title:
            title_control = Container(
                content=Row(
                    controls=[
                        Text(
                            value=title,
                            size=36,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_BACKGROUND,
                        )
                    ],
                ),
            )
            if back_control:
                title_control.content.controls = [back_control] + title_control.content.controls
            body_controls.append(
                title_control
            )

        body_controls += controls

        controls = [
            Container(
                content=Column(
                    controls=[
                        # Header
                        Container(
                            content=Image(
                                src=get_svg(
                                    path='assets/icons/logos/logo_2_full.svg',
                                ),
                                height=56,
                            ),
                            alignment=alignment.center,
                            padding=padding.symmetric(vertical=32, horizontal=64),
                        ),
                        # Body
                        Container(
                            content=Column(
                                controls=body_controls,
                                width=640,
                            ),
                            alignment=alignment.center
                        ),
                    ],
                ),
                padding=10,
            ),
        ]
        return controls
