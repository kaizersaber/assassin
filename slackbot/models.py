from django.db import models
import random

class Team(models.Model):
    name = models.CharField(max_length=200)
    team_id = models.CharField(max_length=20)
    bot_user_id = models.CharField(max_length=20)
    bot_access_token = models.CharField(max_length=100)

class Assassin(object):
    def __init__(self, userID, realName, codeName = "default", dw = "default"):
        self.userID = userID
        self.realName = realName
        self.codeName = codeName
        self.deathWord = dw
        self.kills = 0
        self.hunter = None
        self.target = None
        self.active = False
    
    def __str__(self):
        status = "Inactive"
        target = "None"
        if self.active:
            status = "Active"
            target = self.target.realName
        text = (self.realName +
                "\nCodename: " + self.codeName + 
                "\nDeathword: " + self.deathWord + 
                "\nKills: " + str(self.kills) +
                "\nStatus: " + status +
                "\nTarget: " + target)
        return text

class Lobby(object):
    def __init__(self):
        self.players = []
    
    def add(self, newPlayer):
        self.players.append(newPlayer)
    
    def remove(self,player):
        self.players.remove(player)
    
    def __str__(self):
        lobbyList = sorted(self.players, key = lambda x: x.kills, reverse = True)
        tList = [(p.codeName, p.kills, p.active) for p in lobbyList]
        text = "Codename / Kills / Status\n"
        i = 0
        for t in tList:
            i += 1
            status = "Inactive"
            if t[2]:
                status = "Active"
            text += str(i) + ". " + t[0] + " / " + str(t[1]) + " / " + status + "\n"
        return text

class Game(object):
    def __init__(self, lobby):
        self.loop = []
        for p in lobby.players:
            self.add(p)
        self.head = self.loop[:1]
        self.tail = self.loop[-1:]

    def add(self,player):
        index = random.randint(0,len(self.loop)+1)
        self.loop.insert(index,player)
        self.update()
    
    def remove(self,player):
        player.target = None
        player.hunter = None
        self.loop.remove(player)
        self.update()  
        
    def update(self):
        if self.loop == []:
            return
        else:
            print(self.loop[:1])
            self.head = self.loop[0]
            self.tail = self.loop[-1]
            self.head.hunter = self.tail
            self.tail.target = self.head
            for i in range(len(self.loop)-1):
                self.loop[i].target = self.loop[i+1]
            for i in range(1,len(self.loop)):
                self.loop[i].hunter = self.loop[i-1]
            return

#%%