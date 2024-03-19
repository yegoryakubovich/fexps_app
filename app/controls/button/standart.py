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


from flet_core import ElevatedButton as FletElevatedButton, ButtonStyle, MaterialState, RoundedRectangleBorder, padding, \
    colors


class StandardButton(FletElevatedButton):
    def __init__(
            self,
            bgcolor: str = colors.SECONDARY,
            color: str = colors.BLACK,
            horizontal: int = 12,
            vertical: int = 12,
            **kwargs
    ):
        self.style = ButtonStyle(
            padding=padding.symmetric(horizontal=horizontal, vertical=vertical),
            shape={
                MaterialState.DEFAULT: RoundedRectangleBorder(radius=6),
            },
            overlay_color={
                MaterialState.DEFAULT: colors.PRIMARY_CONTAINER,
                MaterialState.HOVERED: colors.PRIMARY_CONTAINER,
            },
            color={
                MaterialState.DEFAULT: colors.ON_BACKGROUND,
                MaterialState.HOVERED: colors.BACKGROUND,
            },
            shadow_color=None,
        )
        super().__init__(**kwargs)
        self.elevation = 0
        self.bgcolor = bgcolor
        self.color = color
