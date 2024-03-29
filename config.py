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


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_port: int

    version: str = '0.1'
    is_test: bool = True
    language_default: str = 'eng'
    service_id: int = 1
    url: str  # = 'http://api.test.'
    url_telegram: str = 'https://t.me/fexps_manager'

    default_decimal: int = 2
    datetime_format: str = '%d-%m-%y %H:%M'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
