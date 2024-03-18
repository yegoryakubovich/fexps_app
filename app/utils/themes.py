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


from flet_core import Theme, ColorScheme, PageTransitionsTheme, PageTransitionTheme, TextTheme

from flet_manager.utils import Themes


page_transitions = PageTransitionsTheme(
    android=PageTransitionTheme.CUPERTINO,
    ios=PageTransitionTheme.CUPERTINO,
    linux=PageTransitionTheme.CUPERTINO,
    macos=PageTransitionTheme.CUPERTINO,
    windows=PageTransitionTheme.CUPERTINO,
)


themes = Themes(
    light=Theme(
        color_scheme=ColorScheme(
            background='#FFFCEF',
            on_background='#000000',
            primary='#1D1D1D',
            on_primary='#FFFFFF',
            primary_container='#1D1D1D',
            on_primary_container='#7a7a7a',
            secondary='#FFE500',
            secondary_container='#FFE500',
            shadow='#DDDDDD',
        ),
        text_theme=TextTheme(),
        page_transitions=page_transitions,
    ),
    dark=Theme(
        color_scheme=ColorScheme(
            background='#FFFCEF',
            on_background='#000000',
            primary='#1D1D1D',
            on_primary='#FFFFFF',
            primary_container='#1D1D1D',
            on_primary_container='#7a7a7a',
            secondary='#FFE500',
            secondary_container='#FFE500',
            shadow='#DDDDDD',
        ),
        page_transitions=page_transitions,
    ),
)
