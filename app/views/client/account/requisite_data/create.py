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


from flet_core import ScrollMode, Container, Column, Row

from app.controls.layout import ClientBaseView
from app.views.client.account.requisite_data.get import RequisiteDataView
from app.views.client.account.requisite_data.models import RequisiteDataCreateModel


class RequisiteDataCreateView(ClientBaseView):
    route = '/client/requisite/data/create'
    requisite_data_model: RequisiteDataCreateModel

    async def construct(self):
        self.requisite_data_model = RequisiteDataCreateModel(
            session=self.client.session,
            update_async=self.update_async,
            after_close=self.open_requisite_data,
        )
        await self.set_type(loading=True)
        await self.requisite_data_model.construct()
        await self.set_type(loading=False)
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='requisite_data_create_view_title'),
            with_expand=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=self.requisite_data_model.controls,
                        scroll=ScrollMode.AUTO
                    ),
                    expand=True,
                ),
                *self.requisite_data_model.buttons,
            ]
        )

    async def open_requisite_data(self):
        await self.client.change_view(
            view=RequisiteDataView(requisite_data_id=self.requisite_data_model.requisite_data_id),
            delete_current=True,
        )
