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

from flet_core import Row, Text, ScrollMode, colors

from app.controls.information.card import Card
from app.controls.layout import AdminBaseView
from app.controls.navigation.pagination import PaginationWidget
from app.utils import Fonts
from app.views.admin.accounts.get import AccountView


class AccountListView(AdminBaseView):
    route = '/admin/accounts/list/get'
    accounts: list[dict]
    page_account: int = 1
    total_pages: int = 1
    items_per_page: int = 6

    async def construct(self):
        await self.set_type(loading=True)
        response = await self.client.session.api.admin.accounts.search(page=self.page_account)
        self.accounts = response.accounts
        self.total_pages = response.pages
        await self.set_type(loading=False)
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_account_get_list_view_title'),
            main_section_controls=[
                *[
                    Card(
                        controls=[
                            Text(
                                value=account['username'],
                                size=18,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY_CONTAINER,
                            ),
                            Row(
                                controls=[
                                    Text(
                                        value=account['firstname'],
                                        size=13,
                                        font_family=Fonts.REGULAR,
                                        color=colors.ON_PRIMARY_CONTAINER,
                                    ),
                                    Text(
                                        value=account['lastname'],
                                        size=13,
                                        font_family=Fonts.REGULAR,
                                        color=colors.ON_PRIMARY_CONTAINER,
                                    ),
                                ],
                                spacing=5,
                            ),
                        ],
                        on_click=partial(self.account_view, account['id']),
                        color=colors.PRIMARY_CONTAINER,
                    )
                    for account in self.accounts
                ],
                PaginationWidget(
                    current_page=self.page_account,
                    total_pages=self.total_pages,
                    on_back=self.previous_page,
                    on_next=self.next_page,
                    text_back=await self.client.session.gtv(key='back'),
                    text_next=await self.client.session.gtv(key='next'),
                ),
            ]
        )

    async def account_view(self, account_id, _):
        await self.client.change_view(view=AccountView(account_id=account_id))

    async def next_page(self, _):
        if self.page_account < self.total_pages:
            self.page_account += 1
            await self.construct()
            await self.update_async()

    async def previous_page(self, _):
        if self.page_account > 1:
            self.page_account -= 1
            await self.construct()
            await self.update_async()
