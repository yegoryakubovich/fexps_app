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


class TextField(FletTextField):
    def __init__(self, key_question=None, **kwargs):
        super().__init__(**kwargs)
        text_style = TextStyle(
            font_family=Fonts.REGULAR,
            color=colors.ON_BACKGROUND,
        )
        label_style = TextStyle(
            font_family=Fonts.REGULAR,
            color=colors.ON_PRIMARY_CONTAINER,
        )
        self.border_color = colors.PRIMARY_CONTAINER
        self.text_style = text_style
        self.label_style = label_style
        self.key_question = key_question
