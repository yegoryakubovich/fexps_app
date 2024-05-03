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
from fexps_api_client.utils import ApiException
from .create import CommissionPackCreateView
from .get import CommissionPackView


class CommissionPackListView(AdminBaseView):
    route = '/admin/commissions/packs/list/get'
    commissions_packs: list[dict]
    page_count: int = 1
    total_pages: int = 1
    items_per_page: int = 6

    async def construct(self):
        await self.set_type(loading=True)
        try:
            self.commissions_packs = await self.client.session.api.admin.commissions_packs.get_list()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
        await self.set_type(loading=False)
        self.total_pages = (len(self.commissions_packs) - 1) // self.items_per_page + 1
        index_1, index_2 = (self.page_count - 1) * self.items_per_page, self.page_count * self.items_per_page
        self.commissions_packs = self.commissions_packs[index_1:index_2]
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_commissions_packs_get_list_view_title'),
            on_create_click=self.commission_pack_create,
            main_section_controls=[
                *[
                    Card(
                        controls=[
                            Text(
                                value=await self.client.session.gtv(key=commission_pack['name_text']),
                                size=18,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                        on_click=partial(self.commission_pack_view, commission_pack['id']),
                        color=colors.PRIMARY_CONTAINER,
                    )
                    for commission_pack in self.commissions_packs
                ],
                PaginationWidget(
                    current_page=self.page_count,
                    total_pages=self.total_pages,
                    on_back=self.previous_page,
                    on_next=self.next_page,
                    text_back=await self.client.session.gtv(key='back'),
                    text_next=await self.client.session.gtv(key='next'),
                ),
            ]
        )

    async def commission_pack_create(self, _):
        await self.client.change_view(view=CommissionPackCreateView())

    async def commission_pack_view(self, commission_pack_id: int, _):
        await self.client.change_view(view=CommissionPackView(commission_pack_id=commission_pack_id))

    async def next_page(self, _):
        if self.page_count < self.total_pages:
            self.page_count += 1
            await self.construct()
            await self.update_async()

    async def previous_page(self, _):
        if self.page_count > 1:
            self.page_count -= 1
            await self.construct()
            await self.update_async()
