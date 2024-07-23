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

from flet_core import Checkbox, ScrollMode, Container, Row, alignment, Column
from flet_core.dropdown import Option

from app.controls.button import StandardButton, SwitchButton
from app.controls.information import Text
from app.controls.input import TextField, Dropdown
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from app.utils.constants.commission_pack import CommissionPackTelegramTypes
from config import settings
from fexps_api_client.utils import ApiException
from .get import CommissionPackView


class CommissionPackCreateView(AdminBaseView):
    route = '/admin/commissions/packs/create'

    tf_name: TextField
    tf_telegram_chat_id: TextField
    dd_telegram_type: Dropdown
    switch_is_default: SwitchButton

    async def construct(self):
        self.tf_name = TextField(
            label=await self.client.session.gtv(key="name"),
        )
        self.tf_telegram_chat_id = TextField(
            label=await self.client.session.gtv(key="admin_commission_pack_telegram_chat_id"),
        )
        self.dd_telegram_type = Dropdown(
            label=await self.client.session.gtv(key="admin_commission_pack_telegram_type"),
            options=[
                Option(key=CommissionPackTelegramTypes.FEXPS, text=CommissionPackTelegramTypes.FEXPS),
                Option(key=CommissionPackTelegramTypes.SOWAPAY, text=CommissionPackTelegramTypes.SOWAPAY),
            ],
        )
        self.switch_is_default = SwitchButton(
            label=await self.client.session.gtv(key="admin_commission_pack_is_default"),
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key='commissions_packs_create_title'),
            with_expand=True,
            main_section_controls=[
                Container(
                    content=Column(
                        controls=[
                            self.tf_name,
                            self.tf_telegram_chat_id,
                            self.dd_telegram_type,
                            self.switch_is_default,
                        ],
                        scroll=ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='create'),
                                    size=settings.get_font_size(multiple=1.5),
                                    font_family=Fonts.REGULAR,
                                ),
                                on_click=self.create_commission_pack,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
            ],
        )

    async def create_commission_pack(self, _):
        await self.set_type(loading=True)
        try:
            commission_pack_id = await self.client.session.api.admin.commissions_packs.create(
                name=self.tf_name.value,
                telegram_chat_id=self.tf_telegram_chat_id.value,
                telegram_type=self.dd_telegram_type.value,
                is_default=self.switch_is_default.value,
            )
            await self.client.session.get_text_pack()
            await self.set_type(loading=False)
            await self.client.change_view(
                view=CommissionPackView(commission_pack_id=commission_pack_id),
                delete_current=True,
                with_restart=True,
            )
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
