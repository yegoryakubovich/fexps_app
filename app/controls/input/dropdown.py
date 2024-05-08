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


from typing import Optional

from flet_core import Dropdown as FletDropdown, colors, TextStyle
from flet_core.dropdown import Option

from app.utils import Fonts


class Dropdown(FletDropdown):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_color = colors.SECONDARY
        self.text_style = TextStyle(
            font_family=Fonts.REGULAR,
            color=colors.ON_BACKGROUND,
        )
        self.label_style = TextStyle(
            font_family=Fonts.REGULAR,
            color=colors.ON_BACKGROUND,
        )

    def change_options(self, options: Optional[list[Option]] = None, value: Optional[str] = None):
        if not value and len(options) == 1:
            self.value = options[0].key
        self.options = options
