available_items = {
    "fire seeds": 10,
    "water seeds": 10,
    "ice seeds": 10,
}


class Shop:
    """
    A shop is a collection of items that can be bought, they are stored in a dictionary
    With name
    """

    def __init__(self):
        self.items = dict()
