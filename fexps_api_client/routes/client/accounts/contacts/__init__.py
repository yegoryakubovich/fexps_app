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


class ClientAccountContactRoute(BaseRoute):
    prefix = '/contacts'

    async def create(self, contact_id: int, value: str):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'contact_id': contact_id,
                'value': value,
            },
            response_key='id',
        )

    async def get(self, id_: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id': id_,
            },
            response_key='account_contact',
        )

    async def get_list(self):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            response_key='account_contacts',
        )

    async def update(self, id_: int, value: str):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/update',
            parameters={
                'id_': id_,
                'value': value,
            },
        )

    async def delete(self, id_: int):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/delete',
            parameters={
                'id_': id_,
            },
        )
