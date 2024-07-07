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


from flet_core import colors, Row, Image, MainAxisAlignment

from config import settings
from .text import Text
from ..button import StandardButton
from ...utils import Fonts, Icons


class Title(Row):
    def __init__(
            self,
            value: str,
            on_create: callable = None,
            create_name_text: str = None,
            disabled_create: bool = False,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.controls = [
            Text(
                value=value,
                size=settings.get_font_size(multiple=4),
                font_family=Fonts.BOLD,
                color=colors.ON_BACKGROUND,
            ),
        ]
        if on_create:
            self.controls += [
                StandardButton(
                    content=Row(
                        controls=[
                            Image(
                                src=Icons.CREATE,
                                height=16,
                                color=colors.ON_PRIMARY,
                            ),
                            Text(
                                value=create_name_text,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY,
                                size=settings.get_font_size(multiple=1.5),
                            ),
                        ],
                        spacing=4,
                        wrap=True,
                    ),
                    vertical=8,
                    on_click=on_create,
                    disabled=disabled_create,
                    bgcolor=colors.PRIMARY_CONTAINER if disabled_create else colors.PRIMARY,
                ),
            ]
        self.alignment = MainAxisAlignment.SPACE_BETWEEN
