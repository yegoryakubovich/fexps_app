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


from flet_core import Row, Column, colors, ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from app.views.admin.commissions_packs.values.get_list import CommissionPackValueListView
from fexps_api_client import FexpsApiClient


class CommissionPackView(AdminBaseView):
    route = '/admin/commissions/packs/get'
    commission_pack = dict

    def __init__(self, commission_pack_id: int):
        super().__init__()
        self.commission_pack_id = commission_pack_id

    async def build(self):
        await self.set_type(loading=True)
        self.commission_pack = await self.client.session.api.admin.commissions_packs.get(id_=self.commission_pack_id)
        await self.set_type(loading=False)
        self.scroll = ScrollMode.AUTO
        is_default_str = await self.client.session.gtv(
            key=f'commission_pack_{self.commission_pack.is_default}'.lower(),
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key=self.commission_pack.name_text),
            main_section_controls=[
                Column(
                    controls=[
                        Text(
                            value='\n'.join([
                                f'{await self.client.session.gtv(key="name")}: '
                                f'{await self.client.session.gtv(key=self.commission_pack.name_text)}',
                                f'{await self.client.session.gtv(key="commission_pack_is_default")}: '
                                f'{is_default_str}',
                            ]),
                            size=24,
                            font_family=Fonts.MEDIUM,
                            color=colors.ON_BACKGROUND,
                        ),
                        Row(controls=[
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='commissions_packs_values_title'),
                                ),
                                on_click=self.values_get_list_view,
                                expand=True,
                            ),
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='delete'),
                                ),
                                on_click=self.commission_pack_delete,
                                expand=True,
                            ),
                        ]),
                    ],
                ),
            ],
        )

    async def values_get_list_view(self, _):
        await self.client.change_view(view=CommissionPackValueListView(commission_pack_id=self.commission_pack_id))

    async def commission_pack_delete(self, _):
        await self.client.session.api.admin.commissions_packs.delete(id_=self.commission_pack_id)
        await self.client.change_view(go_back=True, with_restart=True)
