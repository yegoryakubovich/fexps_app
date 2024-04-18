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
from app.utils import Fonts, value_to_float


class CommissionPackValueView(AdminBaseView):
    route = '/admin/commissions/packs/value/get'
    commission_pack_value = dict

    def __init__(self, commission_pack_value_id: int):
        super().__init__()
        self.commission_pack_value_id = commission_pack_value_id

    async def construct(self):
        await self.set_type(loading=True)
        self.commission_pack_value = await self.client.session.api.admin.commissions_packs.values.get(
            id_=self.commission_pack_value_id,
        )
        await self.set_type(loading=False)
        self.scroll = ScrollMode.AUTO
        interval_str = (f'{value_to_float(self.commission_pack_value.value_from)}'
                        f' -> '
                        f'{value_to_float(self.commission_pack_value.value_to)}')
        self.controls = await self.get_controls(
            title=interval_str,
            main_section_controls=[
                Column(
                    controls=[
                        Text(
                            value='\n'.join([
                                f'{await self.client.session.gtv(key="commission_pack_value_interval")}: '
                                f'{interval_str}',
                                f'{await self.client.session.gtv(key="commission_pack_value_percent")}: '
                                f'{value_to_float(self.commission_pack_value.percent)}',
                                f'{await self.client.session.gtv(key="commission_pack_value_value")}: '
                                f'{value_to_float(self.commission_pack_value.value)}',
                            ]),
                            size=24,
                            font_family=Fonts.MEDIUM,
                            color=colors.ON_BACKGROUND,
                        ),
                        Row(controls=[
                            StandardButton(
                                content=Text(value=await self.client.session.gtv(key='delete')),
                                on_click=self.commission_pack_value_delete,
                                expand=True,
                            ),
                        ]),
                    ],
                ),
            ],
        )

    async def commission_pack_value_delete(self, _):
        await self.client.session.api.admin.commissions_packs.values.delete(id_=self.commission_pack_value_id)
        await self.client.change_view(go_back=True, with_restart=True)
