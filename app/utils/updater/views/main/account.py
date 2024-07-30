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
from app.utils.updater.schemes import get_account_scheme
from app.views.main.tabs import AccountTab


async def check_update_main_account_view(view: AccountTab, update: bool = True):
    # account
    account = await view.client.session.api.client.accounts.get()
    if update_check(scheme=get_account_scheme, obj_1=view.client.session.account, obj_2=account):
        view.client.session.account = account
        await view.update_account_column(update=update)
    if update:
        await view.account_column.update_async()

