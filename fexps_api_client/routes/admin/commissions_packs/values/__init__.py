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


from fexps_api_client.utils import BaseRoute, RequestTypes


class AdminCommissionPackValueRoute(BaseRoute):
    prefix = '/values'

    async def create(
            self,
            commission_pack_id: int,
            value_from: int,
            value_to: int,
            percent: int,
            value: int
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'commission_pack_id': commission_pack_id,
                'value_from': value_from,
                'value_to': value_to,
                'percent': percent,
                'value': value,
            },
            response_key='id',
        )

    async def get(self, id_: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id_': id_,
            },
            response_key='commission_pack_value',
        )

    async def get_list(self, commission_pack_id: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            parameters={
                'commission_pack_id': commission_pack_id,
            },
            response_key='commissions_packs_values',
        )

    async def delete(self, id_: int):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/delete',
            parameters={
                'id_': id_,
            },
        )
