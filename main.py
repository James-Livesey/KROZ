import re
import json
import urllib.request

import host

from items import *
from rooms import *
from entities import *

TITLE = """\
  _  _______   ____ ______
 | |/ /  __ \\ / __ \\___  /
 | ' /| |__) | |  | | / / 
 |  < |  _  /| |  | |/ /  
 | . \\| | \\ \\| |__| / /__ 
 |_|\\_\\_|  \\_\\\\____/_____|\
"""

print(TITLE)
print("")
print("Welcome to KROZ!")
print("Would you like to play in singleplayer or multiplayer mode?")
print("Multiplayer mode allows you to connect to a server to play.")
print("    (s): singleplayer (default)")
print("    (m): multiplayer")

playersToSpawn = []
isMultiplayer = False
isClient = False
schematic = json.load(open("schematic.json", "r"))

while True:
    gamemode = input("[S/m]? ").lower().strip()

    if gamemode == "s" or gamemode == "":
        isMultiplayer = False

        playersToSpawn.append(input("Enter your player name: "))

        break
    elif gamemode == "m":
        isMultiplayer = True

        print("Do you wish to be a client or a host?")
        print("    (c): client (default)")
        print("    (h): host")

        servemode = input("[C/h]? ").lower().strip()

        if servemode == "c" or servemode == "":
            isClient = True

            break
        elif servemode == "h":
            isClient = False

            break
        else:
            print("Cancelled!")
    else:
        print("Not a valid option!")

print("")

players = []
rooms = []
ingameTime = 0

for i in range(0, len(schematic["rooms"])):
    rooms.append(Room(schematic["rooms"][i]["name"], schematic["rooms"][i]["description"]))

for i in range(0, len(rooms)):
    for direction in schematic["rooms"][i]["directions"]:
        rooms[i].connect(rooms[schematic["rooms"][i]["directions"][direction]], direction, False)
    
    for item in schematic["rooms"][i]["items"]:
        rooms[i].items.append(Item(item["name"], item["description"], item["location"]))
    
    for npc in schematic["rooms"][i]["npcs"]:
        Npc(npc["name"], rooms[i], npc["randomMobility"], npc["defaultReply"])

def pollConnection():
    nextInput = host.handleInput("", False)

    if re.compile(":join (.*)").match(nextInput) != None:
        players.append(Player(re.compile(":join (.*)").match(nextInput).group(1), host.handleInput, host.handleOutput, rooms[0]))

        host.handleOutput(str(len(players) - 1))
        host.inputBuffer.pop(0)
    else:
        for i in range(0, len(rooms)):
            rooms[i].tick(ingameTime)

        players[host.targetPlayer].parseCommand()

        ingameTime += 1

if isMultiplayer and isClient:
    hostAddress = input("Host address: ")
    hostPort = input("Host port: ")
    hostURL = "http://{}:{}".format(hostAddress, hostPort)
    
    playerID = urllib.request.urlopen(hostURL + urllib.parse.quote("/:join {}".format(input("Enter your player name: ")))).read().decode("utf-8").strip()

    print("\n".join(urllib.request.urlopen(hostURL + urllib.parse.quote("/{}/:afterjoin".format(playerID))).read().decode("utf-8").split("\n")[1:]))

    while True:
        print("\n".join(urllib.request.urlopen(hostURL + urllib.parse.quote("/{}/{}".format(playerID, input("\n> ")))).read().decode("utf-8").split("\n")[1:]))
elif isMultiplayer and not isClient:
    host.pollerConnection = pollConnection

    print(host.serve(input("IP address: "), input("Port: ")))
else:
    for player in playersToSpawn:
        players.append(Player(player, input, print, rooms[0]))

    for i in range(0, len(players)):
        players[i].room.describe(players[i])
        players[i].parseCommand()

    while True:
        for i in range(0, len(rooms)):
            rooms[i].tick(ingameTime)

        for i in range(0, len(players)):
            players[i].parseCommand()
        
        ingameTime += 1