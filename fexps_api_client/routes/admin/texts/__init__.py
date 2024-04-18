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
from .packs import AdminTextPackRoute
from .translations import AdminTextTranslationRoute


class AdminTextRoute(BaseRoute):
    prefix = '/texts'

    translations = AdminTextTranslationRoute()
    packs = AdminTextPackRoute()

    async def create(
            self,
            key: str,
            value_default: str,
            create_text_pack: bool = True,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'key': key,
                'value_default': value_default,
                'create_text_pack': create_text_pack,
            },
            response_key='key',
        )

    async def get(self, key: str):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'key': key,
            },
            response_key='text',
        )

    async def get_list(self):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            response_key='texts',
        )

    async def update(
            self,
            key: str,
            value_default: str = None,
            new_key: str = None,
            create_text_pack: bool = True,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/update',
            parameters={
                'key': key,
                'value_default': value_default,
                'new_key': new_key,
                'create_text_pack': create_text_pack,
            },
        )

    async def delete(
            self,
            key: str,
            create_text_pack: bool = True,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/delete',
            parameters={
                'key': key,
                'create_text_pack': create_text_pack,
            },
        )
