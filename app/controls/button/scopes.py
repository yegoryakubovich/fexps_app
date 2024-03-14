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


from flet_core import Card as FletCard, Row as FletRow, Column, colors, Row, \
    MainAxisAlignment, Image, Container

from app.controls.information.text import Text
from app.utils import Icons, Fonts


class ScopeItem:
    name: str
    on_click: callable

    def __init__(self, name: str, on_click: callable = None):
        self.name = name
        self.on_click = on_click


class ScopeCard(FletCard):
    def __init__(self, name: str):
        super().__init__()
        self.icon = Image(
            src=Icons.ADMIN_TEXTS,
            color=colors.ON_PRIMARY_CONTAINER,
            expand=True,
        )
        self.content = Column(controls=[
            Row(
                controls=[self.icon],
                height=170,
                width=200,
                alignment=MainAxisAlignment.CENTER,
            ),
            Row(
                controls=[Text(
                    value=name,
                    size=16,
                    font_family=Fonts.BOLD,
                    color=colors.GREY,
                )],
                height=30,
                width=200,
                alignment=MainAxisAlignment.CENTER,
            ),
        ])


class Scope(FletRow):
    def __init__(self, scopes: list[ScopeItem]):
        super().__init__()
        self.controls = [
            *[Container(
                content=ScopeCard(name=scope.name),
                on_click=scope.on_click,
                height=200,
                width=200,
            ) for scope in scopes]
        ]
        self.alignment = MainAxisAlignment.CENTER
        self.height = 200
