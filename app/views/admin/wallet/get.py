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


from flet_core import colors, Row
from flet_core.dropdown import Option

from app.controls.button import StandardButton
from app.controls.information import Text
from app.controls.input import Dropdown, TextField
from app.controls.layout import AdminBaseView
from app.utils import Fonts, value_to_float
from fexps_api_client.utils import ApiException


class WalletView(AdminBaseView):
    route = '/admin/wallets/get'
    wallet = dict
    commissions_packs = dict

    tf_name: TextField
    dd_commission_pack: Dropdown

    def __init__(self, wallet_id: int):
        super().__init__()
        self.wallet_id = wallet_id

    async def construct(self):
        await self.set_type(loading=True)
        self.wallet = await self.client.session.api.admin.wallets.get(id_=self.wallet_id)
        self.commissions_packs = await self.client.session.api.admin.commissions_packs.get_list()
        await self.set_type(loading=False)
        self.tf_name = TextField(
            label=await self.client.session.gtv(key='wallet_name'),
            value=self.wallet.name,
        )
        wallet_value_str = value_to_float(value=self.wallet.value)
        wallet_value_banned_str = value_to_float(value=self.wallet.value_banned)
        wallet_value_can_minus_str = value_to_float(value=self.wallet.value_can_minus)
        wallet_is_system_str = await self.client.session.gtv(key=f'wallet_is_system_{self.wallet.system}'.lower())
        commission_pack_options = [
            Option(key=commission_pack.id, text=await self.client.session.gtv(key=commission_pack.name_text))
            for commission_pack in self.commissions_packs
        ]
        self.dd_commission_pack = Dropdown(
            options=commission_pack_options,
            label=await self.client.session.gtv(key='wallet_commission_pack'),
            value=self.wallet.commission_pack,
        )
        self.controls = await self.get_controls(
            title=self.wallet.name,
            main_section_controls=[
                self.tf_name,
                Text(
                    value='\n'.join([
                        f'{await self.client.session.gtv(key="wallet_value")}: {wallet_value_str}',
                        f'{await self.client.session.gtv(key="wallet_value_banned")}: {wallet_value_banned_str}',
                        f'{await self.client.session.gtv(key="wallet_value_can_minus")}: {wallet_value_can_minus_str}',
                        f'{await self.client.session.gtv(key="wallet_is_system")}: {wallet_is_system_str}',
                    ]),
                    size=24,
                    font_family=Fonts.MEDIUM,
                    color=colors.ON_BACKGROUND,
                ),
                self.dd_commission_pack,
                Row(
                    controls=[
                        StandardButton(
                            content=Text(
                                value=await self.client.session.gtv(key='save'),
                            ),
                            on_click=self.update_wallet,
                            expand=True,
                        ),
                    ],
                ),

            ],
        )

    async def update_wallet(self, _):
        await self.set_type(loading=True)
        updates = dict(name=None, commission_pack_id=None)
        if self.tf_name.value != self.wallet.name:
            updates.update(name=self.tf_name.value)
        if self.dd_commission_pack.value != self.wallet.commission_pack:
            updates.update(commission_pack_id=self.dd_commission_pack.value)
        try:
            await self.client.session.api.admin.wallets.update(
                id_=self.wallet.id,
                **updates,
            )
            await self.set_type(loading=False)
            await self.construct()
            await self.update_async()
        except ApiException as exception:
            await self.set_type(loading=False)
            return await self.client.session.error(exception=exception)
