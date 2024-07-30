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

    secret_key: str
    version: str = '0.1'
    update_interval: int = 3
    max_accounts: int = 10
    coin_name: str = 'YACoin'
    language_default: str = 'eng'
    url_telegram: str = 'https://t.me/fexps_manager'
    url: str
    chat_url: str
    file_url: str

    test: bool
    test_url: str
    test_chat_url: str
    test_file_url: str

    default_decimal: int = 2
    default_div: int = 100
    datetime_format: str = '%d-%m-%y %H:%M'

    model_config = SettingsConfigDict(env_file='.env')

    def get_url(self):
        if self.test:
            return self.test_url
        return self.url

    def get_chat_url(self):
        if self.test:
            return self.test_chat_url
        return self.chat_url

    def get_file_url(self):
        if self.test:
            return self.test_file_url
        return self.file_url

    @staticmethod
    def get_font_size(multiple: float) -> int:
        return round(8 * multiple)


settings = Settings()
