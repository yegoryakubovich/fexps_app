from flet_core import ElevatedButton
from flet_core import colors

from app.controls.information.text import Text
from app.utils import Fonts


class Chip(ElevatedButton):
    def __init__(self, name: str, key: str,selected, on_select, **kwargs):
        super().__init__(**kwargs)
        self.content = Text(
            value=name,
            size=16,
            font_family=Fonts.BOLD,
            color=colors.ON_BACKGROUND,
        )
        self.bgcolor = colors.GREY_300
        if selected:
            self.bgcolor = colors.SECONDARY
        self.on_click = on_select
        self.key = key
