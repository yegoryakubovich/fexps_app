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

from flet_core import Text, ScrollMode, colors

from app.controls.information.card import Card
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from app.views.admin.roles.create import RoleCreateView
from app.views.admin.roles.get import RoleView


class RoleListView(AdminBaseView):
    route = '/admin/role/list/get'
    roles: list[dict]

    async def construct(self):
        await self.set_type(loading=True)
        self.roles = await self.client.session.api.admin.roles.get_list()
        await self.set_type(loading=False)

        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='admin_role_get_list_view_title'),
            on_create_click=self.create_role,
            main_section_controls=[
                Card(
                    controls=[
                        Text(
                            value=await self.client.session.gtv(key=role['name_text']),
                            size=18,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY_CONTAINER,
                        ),
                    ],
                    on_click=partial(self.role_view, role['id']),
                    color=colors.PRIMARY_CONTAINER,
                )
                for role in self.roles
            ],
         )

    async def create_role(self, _):
        await self.client.change_view(view=RoleCreateView())

    async def role_view(self, role_id, _):
        await self.client.change_view(view=RoleView(role_id=role_id))
