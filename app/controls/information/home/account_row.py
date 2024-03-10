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


from flet_core import Column, colors, Row, CircleAvatar, MainAxisAlignment
from flet_core import Row as FletRow
from flet_core import Text as FletText

from app.controls.information import Text
from app.utils import Fonts


class HomeAccountAvatar(CircleAvatar):
    def __init__(self, username: str, src: str = None, **kwargs):
        super().__init__(**kwargs)
        self.foreground_image_url = src
        self.content = FletText(username[0], size=40, font_family=Fonts.BOLD)
        self.width = 75
        self.height = 75


class HomeAccountRow(FletRow):
    def __init__(self, hello_text: str, name_text: str, avatar: str = None, **kwargs):
        super().__init__(**kwargs)
        self.controls = [
            Column(
                controls=[
                    Row(controls=[Text(
                        value=hello_text,
                        size=16,
                        font_family=Fonts.BOLD,
                        color=colors.GREY,
                    )]),
                    Row(controls=[Text(
                        value=name_text,
                        size=28,
                        font_family=Fonts.BOLD,
                        color=colors.ON_BACKGROUND,
                    )]),
                ],
            ),
            Column(
                controls=[HomeAccountAvatar(username=name_text, src=avatar)],
            )
        ]
        self.alignment = MainAxisAlignment.SPACE_BETWEEN
