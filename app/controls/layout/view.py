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

from flet_core import Container, Image, alignment, padding, BoxShadow, Row, colors
from flet_manager.utils import get_svg
from flet_manager.views import BaseView

from app.controls.information.loading import Loading
from app.controls.information.text import Text
from app.controls.navigation.icon_text_button import IconTextButton
from app.utils import Fonts, Icons
from config import settings


class View(BaseView):
    title = 'Finance Express'
    controls_last: list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = 0
        self.spacing = 0
        self.bgcolor = colors.BACKGROUND

    @staticmethod
    async def get_header():
        return Container(
            content=Image(
                src=get_svg(
                    path='assets/icons/logos/logo_2_full.svg',
                ),
                height=34,
            ),
            alignment=alignment.center,
            padding=padding.symmetric(vertical=18, horizontal=96),
            bgcolor=colors.BACKGROUND,
            shadow=BoxShadow(
                color=colors.SHADOW,
                spread_radius=1,
                blur_radius=20,
            ),
        )

    async def get_title(
            self,
            title: str,
            with_restart: bool = True,
            create_button=None,
            text_key: str = None,
    ):

        async def go_back(_):
            await self.client.change_view(go_back=True, with_restart=with_restart)

        async def go_text(text_key_, _):
            from app.views.admin.texts import TextView
            await self.client.change_view(view=TextView(key=text_key_), delete_current=True)

        controls = []
        if title:
            controls.append(
                Row(
                    controls=[
                        Container(
                            content=Image(
                                src=Icons.BACK,
                                height=30,
                                color=colors.ON_BACKGROUND,
                            ),
                            border_radius=6,
                            ink=True,
                            on_click=go_back,
                        ),
                        Text(
                            value=title,
                            size=settings.get_font_size(multiple=3.5),
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_BACKGROUND,
                            width=None,
                            expand=True,
                        ),
                    ],
                ),

            )

        if text_key:
            controls.append(
                IconTextButton(
                    on_click=partial(go_text, text_key),
                )
            )

        if create_button:
            controls.append(
                Container(
                    content=Row(
                        controls=[
                            Image(
                                src=Icons.CREATE,
                                height=10,
                                color=colors.ON_PRIMARY,
                            ),
                            Text(
                                value='Create',
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY,
                            ),
                        ],
                        spacing=4,
                        wrap=True,
                    ),
                    padding=7,
                    border_radius=24,
                    bgcolor=colors.PRIMARY,
                    on_click=create_button,
                ),
            )

        return Row(
            controls=controls,
            wrap=True,
        )

    async def set_type(self, loading: bool = False):
        if loading:
            self.controls_last = self.controls
            self.controls = [
                Loading(infinity=True, color=colors.PRIMARY),
            ]
            if self.page:
                await self.update_async()
        else:
            if self.controls:
                loading_control = self.controls[0]
                loading_control.infinity = False
                self.controls = self.controls_last
                if self.page:
                    await self.update_async()
            else:
                self.controls = []
                if self.page:
                    await self.update_async()
