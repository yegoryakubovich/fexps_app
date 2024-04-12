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


from base64 import b64encode

from fexps_api_client import FexpsApiClient


async def get_image_src(api: FexpsApiClient, id_str: str) -> str:
    response = await api.client.images.get(id_str=id_str)
    return f'data:image/jpeg;base64,{b64encode(await response.read()).decode()}'
