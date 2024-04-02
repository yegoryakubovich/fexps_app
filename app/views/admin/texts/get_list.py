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


from functools import partial

from flet_core import ScrollMode, colors

from app.controls.information import Text
from app.controls.information.card import Card
from app.controls.layout import AdminBaseView
from app.controls.navigation.pagination import PaginationWidget
from app.utils import Fonts
from .create import TextCreateView
from .get import TextView


class TextListView(AdminBaseView):
    route = '/admin/text/list/get'
    texts: list[dict]
    page_text: int = 1
    total_pages: int = 1
    items_per_page: int = 10

    async def build(self):
        await self.set_type(loading=True)
        self.texts = await self.client.session.api.admin.texts.get_list()
        await self.set_type(loading=False)

        self.total_pages = (len(self.texts) - 1) // self.items_per_page + 1
        self.texts = self.texts[(
                                        self.page_text - 1) * self.items_per_page: self.page_text * self.items_per_page]

        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_text_get_list_view_title'),
            on_create_click=self.create_text,
            main_section_controls=[
                *[
                    Card(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key=text['key']),
                                size=18,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                            Text(
                                value=text['key'],
                                size=10,
                                font_family=Fonts.MEDIUM,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        on_click=partial(self.text_view, text['key']),
                        color=colors.PRIMARY_CONTAINER,
                    )
                    for text in self.texts
                ],
                PaginationWidget(
                    current_page=self.page_text,
                    total_pages=self.total_pages,
                    on_back=self.previous_page,
                    on_next=self.next_page,
                    text_back=await self.client.session.gtv(key='back'),
                    text_next=await self.client.session.gtv(key='next'),
                ),
            ]
        )

    async def create_text(self, _):
        await self.client.change_view(view=TextCreateView())

    async def text_view(self, key, _):
        await self.client.change_view(view=TextView(key=key))

    async def next_page(self, _):
        if self.page_text < self.total_pages:
            self.page_text += 1
            await self.build()
            await self.update_async()

    async def previous_page(self, _):
        if self.page_text > 1:
            self.page_text -= 1
            await self.build()
            await self.update_async()
