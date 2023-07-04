#
#  Nomitron 4 Safe
#
import random 

# Turn Callable
async def rerollCritic(self, payload):
    if payload.get('Author') not in self.moderators: return
    optedPlayers = list(self.Data['Critic']['Opted In'])
    
    for pid in self.Data['PlayerData'].keys():
        isInactive = self.Refs['players'][pid].get_role(self.Refs['roles']['Inactive'].id) is not None
        if pid in optedPlayers and isInactive: optedPlayers.remove(pid)
    
    activePlayers = list(optedPlayers)

    print('   |   Valid Critics:')
    for pid in self.Data['Critic']['Banned']:
        if pid in activePlayers: activePlayers.remove(pid)
        else: print('   |   -', self.Data['PlayerData'][pid]['Name'])
    
    if len(activePlayers) == 0: 
        self.Data['Critic']['Banned'] = []
        activePlayers = optedPlayers
        await self.Refs['channels']['actions'].send('-  The Critic Pool is Reset!')
    if len(activePlayers) == 0: 
        await self.Refs['channels']['actions'].send('-  There are no valid Critic Candidates!')
    else:
        print(len(activePlayers), 'Choices For Critic')
        critic = random.choice(activePlayers)
        self.Data['Critic']['Banned'].append(critic)
        await self.Refs['channels']['actions'].send(f'-  <@{critic}> Is The New Critic!')


async def getNewCritic(self, payload=None):
    if payload is not None and payload.get('Author') not in self.moderators: return
    optedPlayers = list(self.Data['Critic']['Opted In'])
    toDo = []

    for pid in self.Data['PlayerData'].keys():
        isInactive = self.Refs['players'][pid].get_role(self.Refs['roles']['Inactive'].id) is not None
        if pid in optedPlayers and isInactive: optedPlayers.remove(pid)
    
    activePlayers = list(optedPlayers)

    print('   |   Valid Critics:')
    for pid in self.Data['Critic']['Banned']:
        if pid in activePlayers: activePlayers.remove(pid)
        else: print('   |   -', self.Data['PlayerData'][pid]['Name'])
    
    if len(activePlayers) == 0: 
        self.Data['Critic']['Banned'] = []
        activePlayers = optedPlayers
        await self.Refs['channels']['actions'].send('-  The Critic Pool is Reset!')
    if len(activePlayers) == 0: 
        await self.Refs['channels']['actions'].send('-  There are no valid Critic Candidates!')
    else:
        print(len(activePlayers), 'Choices For Critic')
        critic = random.choice(activePlayers)
        self.Data['Critic']['Banned'].append(critic)
        await self.Refs['channels']['actions'].send(f'-  <@{critic}> Is The New Critic!')

    for pid in self.Data['PlayerData'].keys():
        if pid in self.Data['Critic']['Starred']:
            if '⭐' not in self.Data['PlayerData'][pid]['Emojis']:                
                toDo.append( self.Mods.emojiRule.addEmoji(self,pid, '⭐') )
        else:
            if '⭐' in self.Data['PlayerData'][pid]['Emojis']:
                toDo.append( self.Mods.emojiRule.removeEmoji(self, pid, '⭐') )
                
    self.Tasks.update(set( toDo ))
    self.Data['Critic']['Starred'] = []

# Command
async def optIn(self, payload):
    if payload['Channel'] != 'Actions':
        if payload['Author ID'] in self.Data['Critic']['Opted In']:
            await payload['raw'].channel.send('-  You already opted in, but I like your enthusiasm')
        else:
            self.Data['Critic']['Opted In'].append( payload['Author ID'] )
            await payload['raw'].channel.send('-  You are opted in to the Critic Pool')

# Command
async def optOut(self, payload):
    if payload['Channel'] != 'Actions':
        if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
            playerid = payload['Content'].split(' ')[1]
            player = await self.getPlayer(playerid, payload)
            pid = player.id

            if payload['Author ID'] not in self.Data['Critic']['Opted In']:
                await payload['raw'].channel.send(player.name+' already opted out.')
            else:
                self.Data['Critic']['Opted In'].remove( payload['Author ID'] )
                await payload['raw'].channel.send(player.name+' is now opted out of the Critic Pool')

            
        else:
            if payload['Author ID'] not in self.Data['Critic']['Opted In']:
                await payload['raw'].channel.send('You already opted out.')
            else:
                self.Data['Critic']['Opted In'].remove( payload['Author ID'] )
                await payload['raw'].channel.send('You are opted out of the Critic Pool')


"""
Function Called on Reaction
"""
async def on_reaction(self, payload):
    if payload['name'] not in self.moderators: return
    if payload['emoji'] == '✔️' and payload['Channel'] == 'critic-responses':
        print('   |   Starred')
        if (payload['message'].author.id in self.Data['Critic']['Starred']): return
        self.Data['Critic']['Starred'].append(payload['message'].author.id)
        await self.Mods.suitsRule.rewardMethod(self,payload['message'].author.id, 'Next Big Sensation')
        
