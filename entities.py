import re
import random

NO_RANDOM_MOBILITY = -1

class DirectionalityError(Exception):
    pass

class ItemLogisticsError(Exception):
    pass

class Entity:
    def __init__(self, name, room):
        self.name = name
        self.room = room
        self.inventory = []

    def tick(self, ingameTime):
        pass
    
    def pickUp(self, itemName):
        pickedUpItem = False

        for i in range(0, len(self.room.items)):
            if not pickedUpItem:
                if self.room.items[i].name.lower() == itemName.lower():
                    self.room.pickUp(self, self.room.items[i])

                    pickedUpItem = True
        
        if not pickedUpItem:
            raise ItemLogisticsError("No item to pick up")

    def drop(self, itemName):
        droppedItem = False

        for i in range(0, len(self.inventory)):
            if not droppedItem:
                if self.inventory[i].name.lower() == itemName.lower():
                    self.room.drop(self, self.inventory[i])

                    droppedItem = True
        
        if not droppedItem:
            raise ItemLogisticsError("No item to drop")

class Npc(Entity):
    def __init__(self, name, room, randomMobility = NO_RANDOM_MOBILITY, defaultReply = "Hello!"):
        super().__init__(name, room)

        self.randomMobility = randomMobility
        self.defaultReply = defaultReply

        self.room.npcs.append(self)
    
    def go(self, direction):
        if direction in self.room.adjacentRooms:
            self.room.npcs.remove(self)
            self.room = self.room.adjacentRooms[direction]
            self.room.npcs.append(self)
        else:
            raise DirectionalityError("Cannot go in that direction")
    
    def speak(self, player):
        return self.defaultReply.replace("{playerName}", player.name)

    def tick(self, ingameTime):
        if self.randomMobility != NO_RANDOM_MOBILITY:
            if random.randint(0, self.randomMobility) == 0:
                self.go(random.choice(list(self.room.adjacentRooms)))

class Player(Entity):
    def __init__(self, name, ioInput, ioOutput, room):
        super().__init__(name, room)

        self.input = ioInput
        self.output = ioOutput
        self.inventory = []

        self.room.players.append(self)
    
    def help(self):
        self.output("The commands you can type are:")

        self.output("    - help")

        for direction in self.room.adjacentRooms:
            self.output("    - go {}".format(direction))
        
        self.output("    - look around")

        for item in self.room.items:
            self.output("    - pick up {}".format(item.name))
        
        for item in self.inventory:
            self.output("    - drop {}".format(item.name))
        
        for npc in self.room.npcs:
            self.output("    - talk to {}".format(npc.name))

        self.output("    - inventory")
    
    def go(self, direction):
        if direction in self.room.adjacentRooms:
            self.room.players.remove(self)
            self.room = self.room.adjacentRooms[direction]
            self.room.players.append(self)

            self.output("You enter {}.".format(self.room.name))
            self.output("")
            self.room.describe(self)
        else:
            self.output("You cannot go in that direction!")
    
    def lookAround(self):
        self.room.lookAround(self)
    
    def pickUp(self, itemName):
        try:
            super().pickUp(itemName)
        except ItemLogisticsError:
            self.output("There is no {} in this room.".format(itemName.lower()))

    def drop(self, itemName):
        try:
            super().drop(itemName)
        except ItemLogisticsError:
            self.output("You have no {} to drop.".format(itemName.lower()))
    
    def talkTo(self, npcName):
        for npc in self.room.npcs:
            if npcName == npc.name.lower():
                self.output("The {} says: {}".format(npc.name, npc.speak(self)))

                return
        
        self.output("There is no {} to talk to around here.".format(npcName))
    
    def viewInventory(self):
        if len(self.inventory) > 0:
            self.output("In your inventory, you have:")

            for item in self.inventory:
                if re.compile("^[aeiou](.*)$").match(item.name): # If item's name stars with a vowel
                    self.output("    - an {}".format(item.name))
                else:
                    self.output("    - a {}".format(item.name))
        else:
            self.output("You have no items in your inventory.")
        
    def parseCommand(self):
        self.output("")
        command = self.input("> ").lower().strip()
        self.output("")

        if command == ":afterjoin":
            self.room.describe(self)
        elif command == "help":
            self.help()
        elif re.compile("go (.*)").match(command) != None:
            self.go(re.compile("go (.*)").match(command).group(1))
        elif command == "look around":
            self.lookAround()
        elif re.compile("pick up the (.*)").match(command) != None:
            self.pickUp(re.compile("pick up the (.*)").match(command).group(1))
        elif re.compile("pick up (.*)").match(command) != None:
            self.pickUp(re.compile("pick up (.*)").match(command).group(1))
        elif re.compile("drop the (.*)").match(command) != None:
            self.drop(re.compile("drop the (.*)").match(command).group(1))
        elif re.compile("drop (.*)").match(command) != None:
            self.drop(re.compile("drop (.*)").match(command).group(1))
        elif re.compile("talk to (.*)").match(command) != None:
            self.talkTo(re.compile("talk to (.*)").match(command).group(1))
        elif command == "inventory":
            self.viewInventory()
        else:
            self.output("Sorry, I don't understand your command!")