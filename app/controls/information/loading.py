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


from asyncio import sleep, create_task

from flet_core import Image, Column, Stack, MainAxisAlignment, CrossAxisAlignment, Container, UserControl
from flet_manager.utils import get_svg

SLEEP = 0.65
ICONS = {
    1: 300,
}


class Loading(UserControl):
    infinity: bool
    opactity: int
    icon_1: Image
    icon_2: Image
    icon_3: Image

    def __init__(self, color: str, infinity: bool = True, opactity: int = 1):
        super().__init__()
        self.color = color
        self.infinity = infinity
        self.opactity = opactity

    async def did_mount_async(self):
        create_task(self.animate())

    async def animate(self):
        while self.infinity:
            self.opactity = 0 if self.opactity == 1 else 1
            self.icon_1.opacity = self.opactity
            await self.update_async()
            await sleep(SLEEP)

    def build(self):
        svg_1 = get_svg(path=f'assets/icons/logos/logo.svg')
        self.icon_1 = Image(src=svg_1, width=500, height=50, color=self.color, animate_opacity=300, opacity=1)

        self.expand = True
        return Column(
            controls=[
                Stack(
                    controls=[
                        self.icon_1,
                    ],
                ),
                Container(),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            expand=True,
        )
