class RequestInfo:
    id_: int
    type_: str
    state: str
    value: str
    color: str
    date: str

    def __init__(self, id_: int, type_: str, state: str, value: str, color: str, date: str) -> None:
        self.id_ = id_
        self.type_ = type_
        self.state = state
        self.value = value
        self.color = color
        self.date = date
