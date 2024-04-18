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


from datetime import datetime, timedelta
from io import BufferedReader

from addict import Dict
from aiohttp import ClientSession, ContentTypeError, FormData
from furl import furl

from fexps_api_client.utils.exceptions import ApiException
from fexps_api_client.utils.exceptions_manager import exceptions


class RequestTypes:
    GET = 'get'
    POST = 'post'


def rec_keys(dictio, deviation: int):
    if isinstance(dictio, dict):
        for (key, value) in dictio.items():
            if isinstance(value, dict) or isinstance(value, list):
                rec_keys(value, deviation)
                continue
            if key == 'date':
                try:
                    dictio[key] = datetime.strptime(value, '%d-%m-%y %H:%M') + timedelta(hours=deviation)
                except:
                    pass
    elif isinstance(dictio, list):
        for value in dictio:
            if isinstance(value, dict):
                rec_keys(value, deviation)
                continue
    return dictio


class BaseRoute:
    url: str = ''
    prefix: str = ''
    token: str = None

    def __init__(self, url: str = None, token: str = None, deviation: int = 0):
        if not url:
            return

        self.url = url + self.prefix
        self.token = token
        self.deviation = deviation
        for i in dir(self):
            if issubclass(eval(f'type(self.{i})'), BaseRoute):
                route: BaseRoute = eval(f'self.{i}')
                route.__init__(url=self.url, token=self.token, deviation=self.deviation)

    async def create_url(self, prefix: str, parameters: dict) -> str:
        f = furl(url=self.url + prefix)
        f.set(args=parameters)
        return f.url

    async def create_data(self, parameters, token_required, type_):
        parameters = parameters or {}

        json = {}
        url_parameters = {}
        data = FormData()
        if token_required and self.token:
            url_parameters['token'] = self.token

        have_data = False
        for pk, pv in parameters.items():
            if isinstance(pv, BufferedReader) or isinstance(pv, bytes):
                have_data = True
                data.add_field(name=pk, value=pv, filename='1.jpg', content_type='image/jpeg')
                continue

            url_parameters[pk] = pv

        if type_ == RequestTypes.POST and not have_data:
            json = url_parameters
            url_parameters = {}

        return json, url_parameters, data

    async def request(
            self,
            type_: str = RequestTypes.GET,
            prefix: str = '/',
            token_required: bool = True,
            parameters: dict = None,
            response_key: str = None,
    ):
        json, url_parameters, data = await self.create_data(
            parameters=parameters,
            token_required=token_required,
            type_=type_,
        )

        url = await self.create_url(
            prefix=prefix,
            parameters=url_parameters,
        )

        async with ClientSession() as session:
            if type_ == RequestTypes.GET:
                response = await session.get(url=url)
            elif type_ == RequestTypes.POST and url_parameters:
                response = await session.post(url=url, data=data)
            elif type_ == RequestTypes.POST:
                response = await session.post(url=url, json=json)

            try:
                response_json = await response.json()
                rec_keys(response_json, deviation=self.deviation)
                response = Dict(**response_json)
            except ContentTypeError:
                return response

        if response.state == 'successful':
            if response_key:
                response = response.get(response_key)

            return response
        elif response.state == 'error':
            try:
                raise exceptions[response.error.code](message=response.error.message, kwargs=response.error.kwargs)
            except TypeError:
                raise ApiException(message=response.error.message or response.message, kwargs=response.error.kwargs)
