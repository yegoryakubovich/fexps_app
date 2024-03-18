from flet_core import Chip as FletChip
from flet_core import colors

from app.controls.information.text import Text
from app.utils import Fonts


class Chip(FletChip):
    def __init__(self, name: str, key: str, on_select, **kwargs):
        self.label = Text(
            value=name,
            size=16,
            font_family=Fonts.BOLD,
            color=colors.ON_BACKGROUND,
        )
        super().__init__(label=self.label, **kwargs)
        self.key = key
        self.on_select = on_select
        self.selected_color = colors.SECONDARY
        self.bgcolor = colors.GREY_300
