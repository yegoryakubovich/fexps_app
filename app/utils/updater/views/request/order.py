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


from app.utils.updater import update_check
from app.utils.updater.schemes import get_order_scheme
from app.views.client.requests import RequestOrderView


async def check_update_request_order_view(view: RequestOrderView, update: bool = True):
    check_list = []
    order = await view.client.session.api.client.orders.get(id_=view.order_id)
    check_list += [
        update_check(
            scheme=get_order_scheme,
            obj_1=view.order,
            obj_2=order,
        ),
    ]
    if True not in check_list:
        return
    await view.construct()
    if update:
        await view.update_async()
