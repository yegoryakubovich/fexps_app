from flet_core import colors, Row, Container, Image, MainAxisAlignment

from .text import Text
from ...utils import Fonts, Icons


class Title(Row):
    def __init__(self, value: str, on_create: callable = None, create_name_text: str = None, **kwargs):
        super().__init__(**kwargs)
        self.controls = [
            Text(
                value=value,
                size=48,
                font_family=Fonts.BOLD,
                color=colors.ON_BACKGROUND,
            ),
        ]
        if on_create:
            self.controls += [
                Container(
                    content=Row(
                        controls=[
                            Image(
                                src=Icons.CREATE,
                                height=16,
                                color=colors.ON_PRIMARY,
                            ),
                            Text(
                                value=create_name_text,
                                font_family=Fonts.SEMIBOLD,
                                color=colors.ON_PRIMARY,
                                size=20,
                            ),
                        ],
                        spacing=4,
                        wrap=True,
                    ),
                    padding=7,
                    border_radius=24,
                    bgcolor=colors.PRIMARY,
                    on_click=on_create,
                ),
            ]
        self.alignment = MainAxisAlignment.SPACE_BETWEEN
