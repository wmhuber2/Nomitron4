import numpy as np

# Turn Callable, Command
async def resetChallenges(self, payload = None):
    if payload is not None and payload.get('Author') not in self.moderators: return
    
    if payload is not None and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        self.Data['PlayerData'][pid]['Challanged'] = False
        await payload['raw'].channel.send("-  Player Challenges Reset.")
    else:
        for pid in self.Data['PlayerData'].keys():
            self.Data['PlayerData'][pid]['Challanged'] = False
        await self.Refs['channels']['actions'].send("-  Gladitorial Challenges Reset.")


# Turn Callable
async def gladiatorPointCheck(self):
    if  self.Data['Gladiator']['Player'] not in ['', None] and self.Data['Gladiator']['DOB'] + 1 == self.Data['Turn']:
        self.Data['Gladiator']['DOB'] += 1
        self.Data['PlayerData'][self.Data['Gladiator']['Player']]['Friendship Tokens'] += 1

# Command
async def challenge(self, payload): 
    pid = payload['Author ID']
    message = payload['raw']

    if self.Data['PlayerData'][pid]['Challanged']: 
        await message.channel.send(f"-  You must wait until next week to challange again")
        return
    
    if pid == self.Data['Gladiator']['Player']: 
        return
    await self.Mods.suitsRule.rewardMethod(self,pid, 'Challenge')
    self.Data['PlayerData'][pid]['Challanged'] = True
    gladiatorRoll = np.random.randint(1, 101, 1)
    playerRoll    = np.random.randint(1, 25, 1)
    if playerRoll > gladiatorRoll:
        await message.channel.send(f"-  Gladiator: {gladiatorRoll}\nPlayer {playerRoll}\n{payload['Author']} Wins")
        
        player = payload['raw'].author
        gldetr = self.Refs['players'][self.Data['Gladiator']['Player']]

        pid = player.id
        gid = gldetr.id

        if '⚔️' not in self.Data['PlayerData'][pid]['Emojis']:
            await self.Mods.emojiRule.addEmoji(self, pid, '⚔️' )
        
        if '⚔️' in self.Data['PlayerData'][gid]['Emojis']:            
            await self.Mods.emojiRule.removeEmoji(self, gid, '⚔️' )

        print("   |   New Gladiator:",gldetr.nick,"->", player.nick)
        self.Data['Gladiator'] = {'Player': pid, 'DOB':self.Data['Turn']+1}
        await updateEmojis(Data, payload,)
    else: 
        await message.channel.send(f"-  Gladiator: {gladiatorRoll}\nPlayer {playerRoll}\n{payload['Author']} Is Defeated")

# Command
async def setGladiator(self, payload):
    if payload.get('Author') not in self.moderators: return
    
    cont = payload['Content'].strip().split(' ')
    if len(cont) > 1: 
        playerid = payload['Content'].split(' ')[1]

        player = await self.getPlayer(playerid, payload)

        pid = player.id
        gid = self.Data['Gladiator']['Player']

        if '⚔️' not in self.Data['PlayerData'][pid]['Emojis']:
            await self.Mods.emojiRule.addEmoji(self, pid, '⚔️' )
        
        if gid is not None and '⚔️' in self.Data['PlayerData'][gid]['Emojis']:            
            await self.Mods.emojiRule.removeEmoji(self, gid, '⚔️' )
        
        try:print("   |   Set Gladiator:",gldetr.nick,"->", player.nick)
        except: pass

        self.Data['Gladiator'] = {'Player': pid, 'DOB':self.Data['Turn']+1}
        await self.Mods.emojiRule.updateEmojis(self)


