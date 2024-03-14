class TransferInfo:
    type_: str
    description: str
    value: str
    color: str
    date: str

    def __init__(self, type_: str, description: str, value: str, color: str, date: str) -> None:
        self.type_ = type_
        self.description = description
        self.value = value
        self.color = color
        self.date = date