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


class ClientOrderUpdateRoute(BaseRoute):
    prefix = '/updates'

    async def completed(self, id_: int):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/completed',
            parameters={
                'id_': id_,
            },
        )

    async def confirmation(
            self,
            id_: int,
            input_fields: dict,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/confirmation',
            parameters={
                'id_': id_,
                'input_fields': input_fields,
            },
        )

    async def payment(self, id_: int):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/payment',
            parameters={
                'id_': id_,
            },
        )
