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


from flet_core import ElevatedButton
from flet_core import colors

from app.controls.information.text import Text
from app.utils import Fonts


class Chip(ElevatedButton):
    def __init__(self, name: str, key: str, selected, on_select, **kwargs):
        super().__init__(**kwargs)
        self.content = Text(
            value=name,
            size=12,
            font_family=Fonts.BOLD,
            color=colors.ON_PRIMARY,
        )
        self.bgcolor = colors.PRIMARY_CONTAINER
        if selected:
            self.bgcolor = colors.PRIMARY
        self.on_click = on_select
        self.key = key
