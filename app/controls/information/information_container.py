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


from flet_core import Container as FletContainer, colors, ContinuousRectangleBorder, BoxShape


class InformationContainer(FletContainer):
    def __init__(self, content, color=colors.ON_PRIMARY, bgcolor=colors.PRIMARY, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.border_radius = 10
        self.content = content
        self.color = color
        self.bgcolor = bgcolor
        self.on_click = on_click
