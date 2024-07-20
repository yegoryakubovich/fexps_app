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


from flet_core import TextField as FletTextField, colors, TextStyle

from app.utils import Fonts
from config import settings


class TextField(FletTextField):
    def __init__(
            self,
            color: str = colors.ON_BACKGROUND,
            bgcolor: str = colors.BACKGROUND,
            key_question=None,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.border_color = colors.SECONDARY
        self.label_style = TextStyle(
            font_family=Fonts.BOLD,
            color=color,
            size=settings.get_font_size(multiple=1.5),
        )
        self.prefix_style = TextStyle(
            font_family=Fonts.REGULAR,
            color=color,
        )
        self.text_style = TextStyle(
            font_family=Fonts.REGULAR,
            color=color,
        )
        self.suffix_style = TextStyle(
            font_family=Fonts.REGULAR,
            color=color,
        )

        self.bgcolor = bgcolor
        self.selection_color = colors.BLUE_400
        self.key_question = key_question
