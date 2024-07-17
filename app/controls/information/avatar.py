from flet_core import Image, ImageFit, border_radius


class Avatar(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fit = ImageFit.COVER
        self.border_radius = border_radius.all(50)
