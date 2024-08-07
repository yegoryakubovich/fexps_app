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
from app.utils.updater.schemes import get_request_scheme, get_order_list_scheme
from app.views.client.requests import RequestView


async def check_update_request_view(view: RequestView, update: bool = True):
    request = await view.client.session.api.client.requests.get(id_=view.request_id)
    if update_check(scheme=get_request_scheme, obj_1=view.request, obj_2=request):
        view.request = request
        await view.construct()
    if update:
        await view.update_async()
    orders = await view.client.session.api.client.orders.list_get.by_request(request_id=view.request_id)
    if update_check(scheme=get_order_list_scheme, obj_1=view.orders, obj_2=orders):
        view.orders = orders
        await view.update_orders_row()
    if update:
        await view.orders_row.update_async()
