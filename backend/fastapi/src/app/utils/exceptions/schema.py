ITEM_NOT_FOUND = "Item not found"


class DomainError(Exception):
    pass


class ItemNotFound(DomainError):
    def __init__(self) -> None:
        super().__init__(ITEM_NOT_FOUND)
