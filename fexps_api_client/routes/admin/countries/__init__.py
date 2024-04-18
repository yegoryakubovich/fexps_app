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


class AdminCountryRoute(BaseRoute):
    prefix = '/countries'

    async def create(
            self,
            id_str: str,
            name: str,
            language_default: str,
            timezone_default: str,
            currency_default: str,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'id_str': id_str,
                'name': name,
                'language_default': language_default,
                'timezone_default': timezone_default,
                'currency_default': currency_default,
            },
            response_key='id_str',
        )

    async def update(
            self,
            id_str: str,
            name: str = None,
            language_default: str = None,
            timezone_default: str = None,
            currency_default: str = None,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/update',
            parameters={
                'id_str': id_str,
                'name': name,
                'language_default': language_default,
                'timezone_default': timezone_default,
                'currency_default': currency_default,
            },
        )

    async def delete(
            self,
            id_str: str,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/delete',
            parameters={
                'id_str': id_str,
            },
        )
