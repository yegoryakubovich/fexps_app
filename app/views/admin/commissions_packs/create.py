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


import asyncio

from flet_core import Checkbox, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from fexps_api_client.utils import ApiException
from .get import CommissionPackView


class CommissionPackCreateView(AdminBaseView):
    route = '/admin/commissions/packs/create'

    tf_name: TextField
    cb_is_default: Checkbox

    async def build(self):
        self.tf_name = TextField(
            label=await self.client.session.gtv(key='name'),
        )
        self.cb_is_default = Checkbox(
            label=await self.client.session.gtv(key='commission_pack_is_default'),
        )
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='commissions_packs_create_title'),
            main_section_controls=[
                self.tf_name,
                self.cb_is_default,
                StandardButton(
                    content=Text(
                        value=await self.client.session.gtv(key='create'),
                        size=15,
                        font_family=Fonts.REGULAR,
                    ),
                    on_click=self.create_commission_pack,
                ),
            ],
        )

    async def create_commission_pack(self, _):
        await self.set_type(loading=True)
        try:
            commission_pack_id = await self.client.session.api.admin.commissions_packs.create(
                name=self.tf_name.value,
                is_default=self.cb_is_default.value,
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            await asyncio.sleep(0.05)
            await self.client.change_view(
                view=CommissionPackView(commission_pack_id=commission_pack_id),
                delete_current=True,
                with_restart=True,
            )
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
