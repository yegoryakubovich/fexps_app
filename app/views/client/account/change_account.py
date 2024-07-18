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

from flet_core import Column, Container, colors, Row, ScrollMode, Image, MainAxisAlignment

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import ClientBaseView
from app.utils import Fonts, Icons
from config import settings


class ChangeAccountView(ClientBaseView):
    route = '/client/accounts/change'

    accounts_column: Column
    selected_account_id: int

    async def get_account_list(self):
        account_list = []
        for account_tuple in self.client.session.accounts:
            account = account_tuple[2]
            color, bgcolor = colors.ON_PRIMARY_CONTAINER, colors.PRIMARY_CONTAINER
            if account.id == self.client.session.account.id:
                color, bgcolor = colors.ON_PRIMARY, colors.PRIMARY
            account_list += [
                Row(
                    controls=[
                        StandardButton(
                            content=Row(
                                controls=[
                                    Column(
                                        controls=[
                                            Text(
                                                value=f'#{account.id:08}',
                                                size=settings.get_font_size(multiple=2),
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                            Text(
                                                value=f'{account.username}',
                                                size=settings.get_font_size(multiple=3),
                                                font_family=Fonts.SEMIBOLD,
                                                color=color,
                                            ),
                                        ],
                                        expand=True,
                                    ),
                                    StandardButton(
                                        content=Image(src=Icons.LOGOUT, width=32, color=color),
                                        bgcolor=bgcolor,
                                        vertical=0,
                                        horizontal=0,
                                        on_click=partial(
                                            self.client.session.bs_info.open_,
                                            icon=Icons.LOGOUT,
                                            title=await self.client.session.gtv(key='change_account_logout_title'),
                                            description=await self.client.session.gtv(
                                                key='change_account_logout_description',
                                            ),
                                            button_title=await self.client.session.gtv(key='confirm'),
                                            button_on_click=partial(self.account_logout, account.id),
                                        ),
                                    ),
                                ],
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            bgcolor=bgcolor,
                            vertical=24,
                            horizontal=8,
                            on_click=partial(self.account_select, account.id),
                            expand=True,
                        ),
                    ],
                )
            ]
        return account_list

    async def construct(self):
        self.accounts_column = Column(
            controls=await self.get_account_list(),
            scroll=ScrollMode.AUTO,
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='change_account_title'),
            with_expand=True,
            main_section_controls=[
                Container(
                    content=self.accounts_column,
                    expand=True,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='change_account_add'),
                                    size=settings.get_font_size(multiple=1.5),
                                ),
                                on_click=self.account_add,
                                color=colors.ON_PRIMARY_CONTAINER,
                                bgcolor=colors.PRIMARY_CONTAINER,
                                expand=True,
                            ),
                        ],
                    ),
                ),
            ],
        )

    async def account_add(self, _=None):
        if len(self.client.session.tokens) >= settings.max_accounts:
            await self.client.session.bs_error.open_(
                icon=Icons.ERROR,
                title=await self.client.session.gtv(key='change_account_max_error', max_count=settings.max_accounts),
            )
            return
        from app.views.auth.init import InitView
        await self.client.change_view(
            view=InitView(new_login=True),
        )

    async def account_select(self, account_id: int, _=None):
        from app.views.auth.init import InitView
        account_change = await self.client.session.change_account(
            change_view=self.client.change_view,
            account_id=account_id,
        )
        if account_change:
            await self.client.change_view(view=InitView(), delete_current=True)

    async def account_logout(self, account_id: int, _=None):
        from app.views.auth.init import InitView
        for account_tuple in self.client.session.accounts:
            id_, token, account = account_tuple
            if account_id != id_:
                continue
            tokens: list = await self.client.session.get_cs(key='tokens')
            tokens.pop(tokens.index(token))
            await self.client.session.set_cs(key='tokens', value=tokens)
            self.client.session.accounts.pop(self.client.session.accounts.index(token))
            if token == self.client.session.token:
                await self.client.session.set_cs(key='token', value=None)
                await self.client.change_view(view=InitView(), delete_current=True)
                return
            await self.construct()
            await self.update_async()
