from flet_core import CircleAvatar, Text

from app.utils import Fonts


class Avatar(CircleAvatar):
    def __init__(self, username: str, src: str = None, **kwargs):
        super().__init__(**kwargs)
        self.foreground_image_url = src
        self.content = Text(username[0], size=40, font_family=Fonts.BOLD)
        self.width = 75
        self.height = 75
