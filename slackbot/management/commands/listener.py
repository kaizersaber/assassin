from django.core.management.base import BaseCommand
from slackbot.models import Team, Assassin, Lobby, Game
from slackclient import SlackClient
import time
import re


class Command(BaseCommand):
    help = 'Starts the bot for the first'
    def handle(self, *args, **options):
        team = Team.objects.first()
        client = SlackClient("xoxb-335086709553-AVM6StX7HqYoW1xj0IrjXooN")
        self.mainLobby = Lobby()
        self.mainGame = None
        self.userDict = dict()
        self.gameActive = False
        self.teamID = "C9VNBVCA1"
        if client.rtm_connect():
            while True:
                events = client.rtm_read()
                print("%s----%s" % (team, events))
                for event in events:
                    if 'subtype' in event and event['subtype'] == 'bot_message':
                        continue
                    elif 'type' in event and event['type'] == 'message':
                        userID = event['user']
                        channelID = event['channel']
                        msgText = event['text']
                        username = client.server.users[userID].real_name
                        regex = r'^!set (\w+) (\w+)$'
                        if re.match(regex, msgText):
                            matches = re.match(regex, event['text'])
                            codename, dword = matches[1], matches[2]
                            if userID in self.userDict:
                                if self.userDict[userID].active:
                                    client.api_call("chat.postEphemeral",
                                                channel = channelID,
                                                text = "Unable to modify character while in game.",
                                                user = userID)
                                    continue
                                else:
                                    self.setName(userID, codename)
                                    self.setDW(userID, dword)
                            else:
                                self.userDict[userID] = Assassin(userID, username, codename, dword)
                            client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = str(self.userDict[userID]),
                                            user = userID)
                            continue
                        regex = r'^!setname (\w+)$'
                        if re.match(regex, msgText):
                            name = re.match(regex, msgText)[1]
                            if userID in self.userDict:
                                if self.userDict[userID].active:
                                    client.api_call("chat.postEphemeral",
                                                channel = channelID,
                                                text = "Unable to modify codename while in game.",
                                                user = userID)
                                    continue
                                else:
                                    self.setName(userID, name)
                            else:
                                self.userDict[userID] = Assassin(userID, username, codeName = name)
                            client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = str(self.userDict[userID]),
                                            user = userID)
                            continue
                        regex = r'^!setdword (\w+)$'
                        if re.match(regex, msgText):
                            dword = re.match(regex, msgText)[1]
                            if userID in self.userDict:
                                if self.userDict[userID].active:
                                    client.api_call("chat.postEphemeral",
                                                channel = channelID,
                                                text = "Unable to modify deathword while in game.",
                                                user = userID)
                                    continue
                                else:
                                    self.setDW(userID, dword)
                            else:
                                self.userDict[userID] = Assassin(userID, username, dw = dword)
                            client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = str(self.userDict[userID]),
                                            user = userID)
                            continue
                        regex = r'^!self$'
                        if re.match(regex, msgText):
                            if userID in self.userDict:
                                client.api_call("chat.postEphemeral",
                                                channel = channelID,
                                                text = str(self.userDict[userID]),
                                                user = userID)
                            else:
                                client.api_call("chat.postEphemeral",
                                                channel = channelID,
                                                text = "Please create a character using commands !set, !setname or !setdword",
                                                user = userID)
                            continue
                        regex = r'^!joinlobby$'
                        if re.match(regex, msgText):
                            if self.gameActive:
                                client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "Game is already in progress, please wait for the next game.",
                                            user = userID)
                            elif userID in self.userDict:
                                if self.userDict[userID] in self.mainLobby.players:
                                    client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "You are already in the lobby.",
                                            user = userID)
                                else:
                                    self.joinLobby(userID)
                                    client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "You have joined the lobby.",
                                            user = userID)
                                    client.rtm_send_message(self.teamID,
                                                            self.userDict[userID].codeName + " has joined the Lobby.")
                                    client.rtm_send_message(self.teamID,
                                                        str(self.mainLobby))
                            else:
                                client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "Please create a character first by using commands:\n!set, !setname or !setdword",
                                            user = userID)
                            continue
                        regex = r'^!leavelobby$'
                        if re.match(regex, msgText):
                            if self.gameActive:
                                client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "Unable to leave lobby while in game.",
                                            user = userID)
                            elif userID not in self.userDict:
                                client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "Please create a character first by using commands:\n!set, !setname or !setdword.",
                                            user = userID)
                            elif self.userDict[userID] in self.mainLobby.players:
                                self.leaveLobby(userID)
                                client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "You have left the lobby.",
                                            user = userID)
                                client.rtm_send_message(self.teamID,
                                                        self.userDict[userID].codeName + " has left the Lobby.")
                                client.rtm_send_message(self.teamID,
                                                        str(self.mainLobby))
                            else:
                                client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "You are not in the lobby.",
                                            user = userID)
                            continue
                        regex = r'^!scores$'
                        if re.match(regex, msgText):
                            client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = str(self.mainLobby),
                                            user = userID)
                            continue
                        regex = r'^!startgame$'
                        if re.match(regex, msgText):
                            if self.gameActive:
                                client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "Game has already started.",
                                            user = userID)
                            elif len(self.mainLobby.players) < 1:
                                client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "Lobby must have at least 1 player.",
                                            user = userID)
                            else:
                                self.startGame()
                                for p in self.mainLobby.players:
                                    client.api_call("chat.postEphemeral",
                                                channel = self.teamID,
                                                text = "Your target is: " + p.target.realName,
                                                user = p.userID)
                                    client.api_call("chat.postEphemeral",
                                                channel = channelID,
                                                text = str(self.userDict[userID]),
                                                user = userID)
                                client.rtm_send_message(self.teamID,
                                                        "Game has begun.\n\nCurrent Scores:")
                                client.rtm_send_message(self.teamID,
                                                        str(self.mainLobby))
                            continue
                        regex = r'!kill (\w+)\s?(.*)?$'
                        if re.match(regex, msgText):
                            if self.gameActive:
                                if userID not in self.userDict:
                                    client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = "Please create a character first by using commands:\n!set, !setname or !setdword.",
                                            user = userID)
                                elif self.userDict[userID].active:
                                    matches = re.match(regex, msgText)
                                    dw = matches[1]
                                    deathMsg = "\n" + matches[2]
                                    killer = self.userDict[userID]
                                    victim = self.killPlayer(dw, killer)
                                    if victim is not None:
                                        client.api_call("chat.postEphemeral",
                                                channel = self.teamID,
                                                text = "You have been eliminated by " + killer.codeName + " (" + killer.realName + ").",
                                                user = victim.userID)
                                        client.api_call("chat.postEphemeral",
                                                channel = channelID,
                                                text = "Target eliminated.\nYou have " + str(killer.kills) + " confirmed kills.",
                                                user = userID)
                                        client.rtm_send_message(self.teamID, 
                                                                victim.codeName + " (" +
                                                                victim.realName + ")" +
                                                                " has been assassinated by " +
                                                                killer.codeName + "." +
                                                                deathMsg)
                                        client.rtm_send_message(self.teamID,
                                                                str(self.mainLobby))
                                        if len(self.mainGame.loop) < 2:
                                            client.rtm_send_message(self.teamID,
                                                                    "Game over.\n\nFinal Scores:")
                                            client.rtm_send_message(self.teamID,
                                                                    str(self.mainLobby))
                                            client.api_call("chat.postEphemeral",
                                                channel = channelID,
                                                text = "Congratulations! You have won the game.",
                                                user = userID)
                                            self.endGame()
                                        else:
                                            client.api_call("chat.postEphemeral",
                                                channel = channelID,
                                                text = "Your new target is: " + killer.target.realName,
                                                user = userID)
                                    else:
                                        client.api_call("chat.postEphemeral",
                                                    channel = channelID,
                                                    text = "Incorrect death word.",
                                                    user = userID)
                                else:
                                    client.api_call("chat.postEphemeral",
                                                    channel = channelID,
                                                    text = "You cannot kill while eliminated.",
                                                    user = userID)
                            else:
                                client.api_call("chat.postEphemeral",
                                                channel = channelID,
                                                text = "Game has not yet begun.",
                                                user = userID)
                            continue
                        regex = r'^!help$'
                        if re.match(regex, msgText):
                            client.api_call("chat.postEphemeral",
                                            channel = channelID,
                                            text = self.helpText(),
                                            user = userID)
                            continue
                time.sleep(1)
    
    def setName(self,userID,name):
        self.userDict[userID].codeName = name
        
    def setDW(self,userID,dword):
        self.userDict[userID].deathWord = dword
    
    def joinLobby(self, userID):
        newPlayer = self.userDict[userID]
        self.mainLobby.add(newPlayer)
    
    def leaveLobby(self,userID):
        existingPlayer = self.userDict[userID]
        self.mainLobby.remove(existingPlayer)
        
    def startGame(self):
        for p in self.mainLobby.players:
            p.kills = 0
            p.active = True
        self.mainGame = Game(self.mainLobby)
        self.gameActive = True
        
    def endGame(self):
        for p in self.mainLobby.players:
            p.kills = 0
            p.active = False
            p.target = None
            p.hunter = None
        self.gameActive = False
        self.mainLobby.players = []
        self.mainGame = None
        
    def killPlayer(self, dw, killer):
        if killer.target.deathWord == dw:
            victim = killer.target
            self.mainGame.remove(victim)
            victim.active = False
            killer.kills += 1
            return victim
        else:
            return None
    
    def helpText(self):
        text = ("Public Commands:\n" +
                "\n!help\nView this list of commands\n" +
                "\n!scores\nCheck current scores\n" +
                "\nPrivate Commands (DM these commands to AssassinGM):\n" +
                "\n!set <codeName> <deathWord>\nSet your character's codeName and deathWord\n" +
                "\n!setname <codeName>\nSet your character's codeName\n" + 
                "\n!setdword <codeName>\nSet your character's deathWord\n" +
                "\n!self <codeName>\nCheck your character's information\n" +
                "\n!joinlobby\nJoin the lobby\n" +
                "\n!leavelobby\nLeave the lobby\n" +
                "\n!kill <deathWord> <deathMessage>\nKill your target with a deathWord, deathMessage is optional\n")
        return text
            
        
#%%
#from slackclient import SlackClient
#client = SlackClient("xoxb-335086709553-AVM6StX7HqYoW1xj0IrjXooN")
#client.rtm_connect()
#client.server.users
#%%

#%%