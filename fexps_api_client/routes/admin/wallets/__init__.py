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


from fexps_api_client.routes.admin.wallets.bans import AdminWalletBanRoute
from fexps_api_client.utils import BaseRoute, RequestTypes


class AdminWalletRoute(BaseRoute):
    prefix = '/wallets'

    bans = AdminWalletBanRoute()

    async def get(self, id_):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id_': id_,
            },
            response_key='wallet',
        )

    async def get_list(self, account_id: int = None):
        # FIXME
        parameters = {'account_id': account_id} if account_id else {}
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            parameters=parameters,
            response_key='wallets',
        )

    async def update(self, id_: int, name: str = None, commission_pack_id: int = None):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/update',
            parameters={
                'id_': id_,
                'name': name,
                'commission_pack_id': commission_pack_id,
            },
        )
