class Item:
    def __init__(self, name, description, location = "floor"):
        self.name = name
        self.description = description
        self.location = location

    def tick(self, ingameTime):
        pass