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


class ClientOrderListGetRoute(BaseRoute):
    prefix = '/list/get'

    async def main(
            self,
            by_request: bool = False,
            by_requisite: bool = False,
            is_active: bool = False,
            is_finished: bool = False,
    ):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/main',
            parameters={
                'by_request': by_request,
                'by_requisite': by_requisite,
                'is_active': is_active,
                'is_finished': is_finished,
            },
            response_key='orders',
        )

    async def by_request(self, request_id: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/request',
            parameters={
                'request_id': request_id,
            },
            response_key='orders',
        )

    async def by_requisite(self, requisite_id: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/requisite',
            parameters={
                'requisite_id': requisite_id,
            },
            response_key='orders',
        )
