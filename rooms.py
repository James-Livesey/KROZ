import re

class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items = []
        self.players = []
        self.npcs = []
        self.adjacentRooms = {}
    
    def connect(self, room, direction, allowGoingBack = True):
        self.adjacentRooms[direction] = room

        if allowGoingBack:
            if direction == "north":
                room.connect(self, "south", False)
            elif direction == "south":
                room.connect(self, "north", False)
            elif direction == "east":
                room.connect(self, "west", False)
            elif direction == "west":
                room.connect(self, "east", False)
    
    def tick(self, ingameTime):
        for item in self.items:
            item.tick(ingameTime)

        for player in self.players:
            player.tick(ingameTime)
        
        for npc in self.npcs:
            npc.tick(ingameTime)
    
    def describe(self, player):
        player.output(" {}".format(self.name.upper()))
        player.output("-" * (len(self.name) + 2))
        player.output(self.description)
    
    def lookAround(self, player):
        player.output(self.description)

        for direction in self.adjacentRooms:
            print("There is a room to the {}.".format(direction))
        
        for item in self.items:
            if re.compile("^[aeiou](.*)$").match(item.name): # If item's name stars with a vowel
                player.output("There is an {} on the {}.".format(item.name, item.location))
            else:
                player.output("There is a {} on the {}.".format(item.name, item.location))
        
        for npc in self.npcs:
            if re.compile("^[aeiou](.*)$").match(npc.name): # If entity's name stars with a vowel
                player.output("An {} is there.".format(npc.name))
            else:
                player.output("A {} is there.".format(npc.name))
        
        for otherPlayer in self.players:
            if player != otherPlayer:
                player.output("{} is in the room with you.".format(otherPlayer.name))
    
    def pickUp(self, player, item):
        item.location = "backpack"

        self.items.remove(item)
        player.inventory.append(item)

        player.output("You pick up the {}.".format(item.name))
    
    def drop(self, player, item):
        item.location = "floor"

        player.inventory.remove(item)
        self.items.append(item)

        player.output("You drop the {} on the floor.".format(item.name))