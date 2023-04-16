suits = {
        'Hearts'   :  '♥️',
        'Diamonds' :  '♦️',
        'Spades'   :  '♠️',
        'Clubs'    :  '♣️',
    }

async def hearts(self, payload):
    pid = payload['Author ID']

    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |   Setting Suit For ',player.name)   
        if self.Data['PlayerData'][pid].get('Suits') is not None:
            await self.Mods.emojiRule.removeEmoji(self,pid,suits[self.Data['PlayerData'][pid]['Suits']['Suit']])
        self.Data['PlayerData'][pid]['Suits'] = {'Suit':"Hearts", "Exp": 0, "Level":1}
        
    elif payload['Channel'] == 'actions':
        print('   |   Setting Suit For ',pid)     
        if self.Data['PlayerData'][pid].get('Suits') is not None:
            await self.Mods.emojiRule.removeEmoji(self,pid,suits[self.Data['PlayerData'][pid]['Suits']['Suit']])
        self.Data['PlayerData'][pid]['Suits'] = {'Suit':"Hearts", "Exp": 0, "Level":1}

    else:
        await self.dm(pid, "You must put your commands in #Actions")

async def diamonds(self, payload):
    pid = payload['Author ID']

    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |   Setting Suit For ',player.name)        
        if self.Data['PlayerData'][pid].get('Suits') is not None:
            await self.Mods.emojiRule.removeEmoji(self,pid,suits[self.Data['PlayerData'][pid]['Suits']['Suit']])
        self.Data['PlayerData'][pid]['Suits'] = {'Suit':"Diamonds", "Exp": 0, "Level":1}

    elif payload['Channel'] == 'actions':
        print('   |   Setting Suit For ',pid)     
        if self.Data['PlayerData'][pid].get('Suits') is not None:
            await self.Mods.emojiRule.removeEmoji(self,pid,suits[self.Data['PlayerData'][pid]['Suits']['Suit']])
        self.Data['PlayerData'][pid]['Suits'] = {'Suit':"Diamonds", "Exp": 0, "Level":1}

    else:
        await self.dm(pid, "You must put your commands in #Actions")

async def spades(self, payload):
    pid = payload['Author ID']

    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |   Setting Suit For ',player.name)        
        if self.Data['PlayerData'][pid].get('Suits') is not None:
            await self.Mods.emojiRule.removeEmoji(self,pid,suits[self.Data['PlayerData'][pid]['Suits']['Suit']])
        self.Data['PlayerData'][pid]['Suits'] = {'Suit':"Spades", "Exp": 0, "Level":1}


    elif payload['Channel'] == 'actions':
        print('   |   Setting Suit For ',pid)     
        if self.Data['PlayerData'][pid].get('Suits') is not None:
            await self.Mods.emojiRule.removeEmoji(self,pid,suits[self.Data['PlayerData'][pid]['Suits']['Suit']])
        self.Data['PlayerData'][pid]['Suits'] = {'Suit':"Spades", "Exp": 0, "Level":1}

    else:
        await self.dm(pid, "You must put your commands in #Actions")

async def clubs(self, payload):
    pid = payload['Author ID']

    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |   Setting Suit For ',player.name)        
        if self.Data['PlayerData'][pid].get('Suits') is not None:
            await self.Mods.emojiRule.removeEmoji(self,pid,suits[self.Data['PlayerData'][pid]['Suits']['Suit']])
        self.Data['PlayerData'][pid]['Suits'] = {'Suit':"Clubs", "Exp": 0, "Level":1}

    elif payload['Channel'] == 'actions':
        print('   |   Setting Suit For ',pid)     
        if self.Data['PlayerData'][pid].get('Suits') is not None:
            await self.Mods.emojiRule.removeEmoji(self,pid,suits[self.Data['PlayerData'][pid]['Suits']['Suit']])
        self.Data['PlayerData'][pid]['Suits'] = {'Suit':"Clubs", "Exp": 0, "Level":1}

    else:
        await self.dm(pid, "You must put your commands in #Actions")

async def addExperience(self, payload):
    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        text = payload['Content'].split(' ')
        playerid = text[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        amount = int(text[2])
        print('   |   Setting Exp For ',player.name)        
        await addExp(self, pid, amount)

async def addExp(self, pid, exp):
    plevel = self.Data['PlayerData'][pid]['Suits']['Level']
    self.Data['PlayerData'][pid]['Suits']['Exp'] += exp
    if self.Data['PlayerData'][pid]['Suits']['Exp'] > 320:
        self.Data['PlayerData'][pid]['Suits']['Exp'] = 320

    for i in range(1,6):
        if self.Data['PlayerData'][pid]['Suits']['Exp'] <= 10 * (2**(i)):
            self.Data['PlayerData'][pid]['Suits']['Level'] = i
            break
   
    if self.Data['PlayerData'][pid]['Suits']['Level'] >= 5 and plevel < 5:
        await self.Mods.emojiRule.addEmoji(self,pid,suits[self.Data['PlayerData'][pid]['Suits']['Suit']])

async def resetMethods(self):
    for pid in self.Data['PlayerData'].keys():
        if self.Data['PlayerData'][pid].get('Suits') is not None:
            self.Data['PlayerData'][pid]['Ways To Get Exp'] = {
                'Vote':2,
                'Challenge':10,
                'Next Big Sensation':20,
                'Buddy':5
            }
async def rewardMethod(self, pid, method):
    if self.Data['PlayerData'][pid].get('Ways To Get Exp') is None:
        self.Data['PlayerData'][pid]['Ways To Get Exp'] = {
                'Vote':2,
                'Challenge':10,
                'Next Big Sensation':20,
                'Buddy':5
            }
    if self.Data['PlayerData'][pid].get('Suits') is not None:
        if method in self.Data['PlayerData'][pid]['Ways To Get Exp']:
            if method == 'Vote': self.Data['PlayerData'][pid]['Union Vote Counter'] += 1
            await addExp(self, pid,  self.Data['PlayerData'][pid]['Ways To Get Exp'][method])
            del self.Data['PlayerData'][pid]['Ways To Get Exp'][method]