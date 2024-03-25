from flet_core import colors, Row

from .text import Text
from ...utils import Fonts


class SubTitle(Row):
    def __init__(self, value: str, **kwargs):
        super().__init__(**kwargs)
        self.controls = [
            Text(
                value=value,
                size=32,
                font_family=Fonts.BOLD,
                color=colors.ON_BACKGROUND,
            )
        ]
