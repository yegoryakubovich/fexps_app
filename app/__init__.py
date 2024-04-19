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


from os.path import abspath

from flet_manager import App

from app.views import views, InitView
from .utils import fonts, themes
from .utils.logger import config_logger


def create_app():
    config_logger()
    app = App(
        name='Finance Express',
        views=views,
        view_main=InitView,
        assets_dir=abspath('assets'),
        fonts=fonts,
        themes=themes,
    )
    return app.fastapi
