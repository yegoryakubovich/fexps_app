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


from flet_core import padding, Container, Row, Image, border_radius, colors

from app.controls.information.text import Text
from app.utils import Fonts


class ListItemButton(Container):
    def __init__(self, name: str, icon, font_size: int = 16, on_click=None, url=None):
        super().__init__(
            content=Row(
                controls=[
                    Image(
                        src=icon,
                        width=28,
                    ),
                    Text(
                        value=name,
                        font_family=Fonts.REGULAR,
                        size=font_size,
                        color=colors.ON_BACKGROUND,
                    ),
                ],
                spacing=12,
            ),
            padding=padding.symmetric(vertical=4),
            ink=True,
            on_click=on_click,
            url=url,
            border_radius=border_radius.all(6),
        )
