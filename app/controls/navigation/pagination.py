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


from typing import Callable

from flet_core import Container, Row, colors

from app.controls.button import StandardButton
from app.controls.information import Text
from app.utils import Fonts


class PaginationWidget(Container):
    def __init__(
            self,
            text_next: str,
            text_back: str,
            current_page: int,
            total_pages: int,
            on_back: Callable,
            on_next: Callable,
            disable_next_button: bool = True
    ):
        self.current_page = current_page
        self.total_pages = total_pages
        self.on_previous = on_back
        self.on_next = on_next
        self.disable_next_button = disable_next_button
        super().__init__()
        self.content = Row(
            controls=[
                StandardButton(
                    content=Text(value=text_back),
                    on_click=self.on_previous,
                    disabled=self.current_page <= 1,
                ),
                Text(
                    value=f'{self.current_page}/{self.total_pages}',
                    size=18,
                    font_family=Fonts.SEMIBOLD,
                    color=colors.ON_BACKGROUND,
                ),
                StandardButton(
                    content=Text(value=text_next),
                    on_click=self.on_next,
                    disabled=self.disable_next_button and self.current_page >= self.total_pages,
                ),
            ],
        )
