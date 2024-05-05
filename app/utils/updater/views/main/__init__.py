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
from app.utils.updater.views.main.account import check_update_main_account_view
from app.utils.updater.views.main.home import check_update_main_home_view
from app.utils.updater.views.main.request import check_update_main_request_view
from app.utils.updater.views.main.requisite import check_update_main_requisite_view
from app.views.main.main import MainView
from app.views.main.tabs import HomeTab, RequestTab, RequisiteTab, AccountTab


async def check_update_main_view(view: MainView):
    for tab in view.tabs:
        tab_view = tab.controls[0]
        if isinstance(tab_view, HomeTab):
            await check_update_main_home_view(tab_view, update=tab == view.tab_selected)
        elif isinstance(tab_view, RequestTab):
            await check_update_main_request_view(tab_view, update=tab == view.tab_selected)
        elif isinstance(tab_view, RequisiteTab):
            await check_update_main_requisite_view(tab_view, update=tab == view.tab_selected)
        elif isinstance(tab_view, AccountTab):
            await check_update_main_account_view(tab_view, update=tab == view.tab_selected)
