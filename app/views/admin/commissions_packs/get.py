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


from flet_core import Row, Column, ScrollMode, Container, alignment, colors
from flet_core.dropdown import Option

from app.controls.button import StandardButton, SwitchButton
from app.controls.information import Text
from app.controls.input import TextField, Dropdown
from app.controls.layout import AdminBaseView
from app.utils import Fonts
from app.utils.constants.commission_pack import CommissionPackTelegramTypes
from app.views.admin.commissions_packs.values.get_list import CommissionPackValueListView
from config import settings
from fexps_api_client.utils import ApiException


class CommissionPackView(AdminBaseView):
    route = '/admin/commissions/packs/get'

    commission_pack = dict

    tf_name: TextField
    tf_telegram_chat_id: TextField
    dd_telegram_type: Dropdown
    switch_is_default: SwitchButton

    def __init__(self, commission_pack_id: int):
        super().__init__()
        self.commission_pack_id = commission_pack_id

    async def construct(self):
        await self.set_type(loading=True)
        self.commission_pack = await self.client.session.api.admin.commissions_packs.get(id_=self.commission_pack_id)
        await self.set_type(loading=False)
        self.tf_name = TextField(
            label=await self.client.session.gtv(key="name"),
            value=await self.client.session.gtv(key=self.commission_pack.name_text),
        )
        self.tf_telegram_chat_id = TextField(
            label=await self.client.session.gtv(key="admin_commission_pack_telegram_chat_id"),
            value=self.commission_pack.telegram_chat_id,
        )
        self.dd_telegram_type = Dropdown(
            label=await self.client.session.gtv(key="admin_commission_pack_telegram_type"),
            options=[
                Option(key=CommissionPackTelegramTypes.FEXPS, text=CommissionPackTelegramTypes.FEXPS),
                Option(key=CommissionPackTelegramTypes.SOWAPAY, text=CommissionPackTelegramTypes.SOWAPAY),
            ],
            value=self.commission_pack.telegram_type,
        )
        self.switch_is_default = SwitchButton(
            label=await self.client.session.gtv(key="admin_commission_pack_is_default"),
            value=self.commission_pack.is_default,
        )
        self.controls = await self.get_controls(
            title=await self.client.session.gtv(key=self.commission_pack.name_text),
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
                                    value=await self.client.session.gtv(key='commissions_packs_values_title'),
                                    size=settings.get_font_size(multiple=1.5),
                                    font_family=Fonts.REGULAR,
                                ),
                                on_click=self.values_get_list_view,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
                Container(
                    content=Row(
                        controls=[
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='save'),
                                    size=settings.get_font_size(multiple=1.5),
                                    font_family=Fonts.REGULAR,
                                ),
                                on_click=self.commission_pack_update,
                                expand=True,
                            ),
                            StandardButton(
                                content=Text(
                                    value=await self.client.session.gtv(key='delete'),
                                    size=settings.get_font_size(multiple=1.5),
                                    font_family=Fonts.REGULAR,
                                    color=colors.BLACK,
                                ),
                                bgcolor=colors.RED,
                                on_click=self.commission_pack_delete,
                                expand=True,
                            ),
                        ],
                    ),
                    alignment=alignment.bottom_center,
                ),
            ],
        )

    async def values_get_list_view(self, _):
        await self.client.change_view(view=CommissionPackValueListView(commission_pack_id=self.commission_pack_id))

    async def commission_pack_update(self, _):
        try:
            await self.client.session.api.admin.commissions_packs.update(
                id_=self.commission_pack_id,
                name=self.tf_name.value,
                telegram_chat_id=self.tf_telegram_chat_id.value,
                telegram_type=self.dd_telegram_type.value,
                is_default=self.switch_is_default.value,
            )
            await self.client.session.get_text_pack()
            await self.client.change_view(go_back=True, with_restart=True)
        except ApiException as exception:
            return await self.client.session.error(exception=exception)

    async def commission_pack_delete(self, _):
        await self.client.session.api.admin.commissions_packs.delete(id_=self.commission_pack_id)
        await self.client.change_view(go_back=True, with_restart=True)
