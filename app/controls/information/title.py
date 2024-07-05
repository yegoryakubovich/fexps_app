from flet_core import colors, Row, Container, Image, MainAxisAlignment

from .text import Text
from ..button import StandardButton
from ...utils import Fonts, Icons


class Title(Row):
    def __init__(
            self,
            value: str,
            on_create: callable = None,
            create_name_text: str = None,
            disabled_create: bool = False,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.controls = [
            Text(
                value=value,
                size=32,
                font_family=Fonts.BOLD,
                color=colors.ON_BACKGROUND,
            ),
        ]
        if on_create:
            self.controls += [
                StandardButton(
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
                                size=14,
                            ),
                        ],
                        spacing=4,
                        wrap=True,
                    ),
                    vertical=8,
                    on_click=on_create,
                    disabled=disabled_create,
                    bgcolor=colors.PRIMARY_CONTAINER if disabled_create else colors.PRIMARY,
                ),
            ]
        self.alignment = MainAxisAlignment.SPACE_BETWEEN
