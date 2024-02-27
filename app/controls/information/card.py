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


from flet_core import Card as FletCard, Container, Column, colors


class Card(FletCard):
    def __init__(self, controls, on_click, **kwargs):
        super().__init__(**kwargs)
        self.margin = 0
        self.width = 3000
        self.content = Container(
            content=Column(
                controls=controls,
            ),
            ink=True,
            padding=10,
            border_radius=10,
            on_click=on_click
        )
        self.color = colors.SECONDARY
