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


from fexps_api_client.utils import ApiException

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import AdminBaseView


class AccountRoleView(AdminBaseView):
    route = '/admin/account/role/get'
    role = dict

    def __init__(self, account_id, role, role_id):
        super().__init__()
        self.account_id = account_id
        self.role_id = role_id
        self.role = role

    async def build(self):
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key=self.role['name_text']),
            main_section_controls=[
                StandardButton(
                    content=Text(
                        value=await self.client.session.gtv(key='delete'),
                    ),
                    on_click=self.delete_role,
                    expand=True,
                ),
            ],
        )

    async def delete_role(self, _):
        await self.set_type(loading=True)
        try:
            await self.client.session.api.admin.accounts.roles.delete(
                id_=self.role_id,
            )
            await self.set_type(loading=False)
            await self.client.change_view(go_back=True, with_restart=True, delete_current=True)
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
