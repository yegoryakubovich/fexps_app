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


from app.controls.layout import AdminBaseView
from fexps_api_client import FexpsApiClient


class RequisiteView(AdminBaseView):
    route = '/client/requisite/get'
    requisite = dict

    def __init__(self, requisite_id: int):
        super().__init__()
        self.requisite_id = requisite_id

    async def build(self):
        await self.set_type(loading=True)
        self.requisite = await self.client.session.api.client.requisite.get(id_=self.requisite_id)
        await self.set_type(loading=False)
