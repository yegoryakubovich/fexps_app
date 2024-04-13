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


from flet_core import ScrollMode

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import TextField
from app.controls.layout import AdminBaseView
from app.utils import Fonts, validation_float, value_to_int, Error
from fexps_api_client.utils import ApiException
from .get import CommissionPackValueView


class CommissionPackValueCreateView(AdminBaseView):
    route = '/admin/commissions/packs/values/create'

    tf_value_from: TextField
    tf_value_to: TextField
    tf_percent: TextField
    tf_value: TextField

    def __init__(self, commission_pack_id: int):
        super().__init__()
        self.commission_pack_id = commission_pack_id

    async def build(self):
        self.tf_value_from = TextField(
            label=await self.client.session.gtv(key='commission_pack_value_from'),
        )
        self.tf_value_to = TextField(
            label=await self.client.session.gtv(key='commission_pack_value_to'),
        )
        self.tf_percent = TextField(
            label=await self.client.session.gtv(key='commission_pack_value_percent'),
        )
        self.tf_value = TextField(
            label=await self.client.session.gtv(key='commission_pack_value_value'),
        )
        self.scroll = ScrollMode.AUTO
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='commissions_packs_create_title'),
            main_section_controls=[
                self.tf_value_from,
                self.tf_value_to,
                self.tf_percent,
                self.tf_value,
                StandardButton(
                    content=Text(
                        value=await self.client.session.gtv(key='create'),
                        size=15,
                        font_family=Fonts.REGULAR,
                    ),
                    on_click=self.create_commission_pack_value,
                ),
            ],
        )

    async def create_commission_pack_value(self, _):
        for field in [self.tf_value_from, self.tf_value_to, self.tf_percent, self.tf_value]:
            if not await Error.check_field(self, field, check_float=True):
                await self.set_type(loading=False)
                return
        await self.set_type(loading=True)
        try:
            commission_pack_value_id = await self.client.session.api.admin.commissions_packs.values.create(
                commission_pack_id=self.commission_pack_id,
                value_from=value_to_int(self.tf_value_from.value),
                value_to=value_to_int(self.tf_value_to.value),
                percent=value_to_int(self.tf_percent.value),
                value=value_to_int(self.tf_value.value),
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            await self.client.change_view(
                view=CommissionPackValueView(commission_pack_value_id=commission_pack_value_id),
                delete_current=True,
                with_restart=True,
            )
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
