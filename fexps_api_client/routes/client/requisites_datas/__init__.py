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


class ClientRequisiteDataRoute(BaseRoute):
    prefix = '/requisites_datas'

    async def create(self, name: str, method_id: int, fields: dict):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'name': name,
                'method_id': method_id,
                'fields': fields,
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
            response_key='requisite_data',
        )

    async def get_list(self):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            response_key='requisite_datas',
        )

    async def update(self, id_: int, fields: dict):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/update',
            parameters={
                'id_': id_,
                'fields': fields,
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
