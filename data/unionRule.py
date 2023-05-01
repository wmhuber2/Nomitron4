async def unionize(self, payload):
    ActivePlayers = [] 
    for player in self.Refs['roles']['Player'].members:
        pid = player.id
        if 'Union Vote Counter' not in self.Data['PlayerData'][pid]:
            self.Data['PlayerData'][pid]['Union Vote Counter' ]
        self.Data['PlayerData'][pid]['Union Vote Counter'] = 0

        if player not in self.Refs['roles']['Inactive'].members:
            ActivePlayers.append(pid)
    union1 = []
    union2 = []
    union3 = []

    for i in range(len(ActivePlayers)):
        if i % 3 == 0: union1.append(ActivePlayers.pop())
        if i % 3 == 1: union2.append(ActivePlayers.pop())
        if i % 3 == 2: union3.append(ActivePlayers.pop())
    
    self.Data['Unions']={
        'Union 1': union1,
        'Union 2': union2,
        'Union 3': union3,
    }

    for p in union1:
        await self.Refs['players'][p].add_roles(   self.Refs['roles']['Union 1']) 
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 2']) 
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 3']) 
    
    for p in union2:
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 1']) 
        await self.Refs['players'][p].add_roles(   self.Refs['roles']['Union 2']) 
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 3']) 
    
    for p in union3:
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 1']) 
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 2']) 
        await self.Refs['players'][p].add_roles(   self.Refs['roles']['Union 3']) 

    msg = "New Unions Formed: \n" \
          "Union 1: "+ ' '.join([self.Refs['players'][p].mention for p in union1])+"\n" \
          "Union 2: "+ ' '.join([self.Refs['players'][p].mention for p in union2])+"\n" \
          "Union 3: "+ ' '.join([self.Refs['players'][p].mention for p in union3])+"\n" 
    await self.Refs['channels']['actions'].send(msg)


async def unionBreak(self,payload):
    if payload.get('Author') not in self.moderators: return
    playerid = payload['Content'].split(' ')[1]
    player = await self.getPlayer(playerid, payload)
    pid = player.id

    if 'Union State' not in self.Data['PlayerData'][pid]:
        self.Data['PlayerData'][pid]['Union State']
    self.Data['PlayerData'][pid]['Union State'] = 'Will Be On Break'

async def makeBreak(self, pid):
    for pid in self.Data['PlayerData'].keys():
        if self.Data['PlayerData'][pid]['Union State'] == 'Will Be On Break':
            self.Data['PlayerData'][pid]['Union State'] = 'Break'
            await self.Mods.tokensRule.addTokens(self, pid, 1)
        else:
            self.Data['PlayerData'][pid]['Union State'] = 'None'

async def unionLunch(self,payload):
    if payload.get('Author') not in self.moderators: return
    playerid = payload['Content'].split(' ')[1]
    player = await self.getPlayer(playerid, payload)
    pid = player.id

    if 'Union State' not in self.Data['PlayerData'][pid]:
        self.Data['PlayerData'][pid]['Union State']
    self.Data['PlayerData'][pid]['Union State'] = 'Lunch'

async def unionVote(self,payload):
    if payload.get('Author') not in self.moderators: return
    playerid = payload['Content'].split(' ')[1]
    try: toset = int(payload['Content'].split(' ')[2])
    except ValueError: return
    player = await self.getPlayer(playerid, payload)
    pid = player.id
    self.Data['PlayerData'][pid]['Union Vote Counter'] = toset
