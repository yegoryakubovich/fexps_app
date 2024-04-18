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


class ClientTransfersRoute(BaseRoute):
    prefix = '/transfers'

    async def create(
            self,
            wallet_from_id: int,
            wallet_to_id: int,
            value: int,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'wallet_from_id': wallet_from_id,
                'wallet_to_id': wallet_to_id,
                'value': value,
            },
            response_key='id',
        )

    async def get(self, id_):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id_': id_,
            },
            response_key='transfer',
        )

    async def search(
            self,
            wallet_id: int,
            is_sender: bool = True,
            is_receiver: bool = True,
            page: int = 1,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/search',
            parameters={
                'wallet_id': wallet_id,
                'is_sender': is_sender,
                'is_receiver': is_receiver,
                'page': page,
            },
        )
