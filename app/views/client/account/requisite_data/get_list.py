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
from app.controls.input import TextField
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from app.views.client.account.requisite_data.create import RequisiteDataCreateView
from app.views.client.account.requisite_data.get import RequisiteDataView


class RequisiteDataListView(AdminBaseView):
    route = '/admin/requisite/data/list/get'
    requisites_datas: list[dict]
    tf_search = TextField

    async def build(self):
        await self.set_type(loading=True)
        self.requisites_datas = await self.client.session.api.client.requisite_data.get_list()
        await self.set_type(loading=False)

        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='requisite_data_get_list_view_title'),
            on_create_click=self.create_requisite_data,
            main_section_controls=[
                Card(
                    controls=[
                        Text(
                            value=requisite_data['name'],
                            size=18,
                            font_family=Fonts.SEMIBOLD,
                            color=colors.ON_PRIMARY,
                        ),
                    ],
                    on_click=partial(self.requisite_data_view, requisite_data['id']),
                )
                for requisite_data in self.requisites_datas
            ]
        )

    async def requisite_data_view(self, requisite_data_id: int, _):
        await self.client.change_view(view=RequisiteDataView(requisite_data_id=requisite_data_id))

    async def create_requisite_data(self, _):
        await self.client.change_view(view=RequisiteDataCreateView())
