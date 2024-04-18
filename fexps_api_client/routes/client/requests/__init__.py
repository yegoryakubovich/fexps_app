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
from .updates import ClientRequestUpdateRoute


class ClientRequestRoute(BaseRoute):
    prefix = '/requests'

    updates = ClientRequestUpdateRoute()

    async def create(
            self,
            wallet_id: int,
            type_: str,
            input_method_id: int = None,
            input_currency_value: int = None,
            input_value: int = None,
            output_requisite_data_id: int = None,
            output_currency_value: int = None,
            output_value: int = None,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'wallet_id': wallet_id,
                'type_': type_,
                'input_method_id': input_method_id,
                'input_currency_value': input_currency_value,
                'input_value': input_value,
                'output_requisite_data_id': output_requisite_data_id,
                'output_currency_value': output_currency_value,
                'output_value': output_value,
            },
            response_key='id',
        )

    async def get(
            self,
            id_: int,
    ):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id_': id_,
            },
            response_key='request',
        )

    async def search(
            self,
            is_completed: bool = False,
            is_canceled: bool = False,
            page: int = 1,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/search',
            parameters={
                'is_completed': is_completed,
                'is_canceled': is_canceled,
                'page': page,
            },
        )
