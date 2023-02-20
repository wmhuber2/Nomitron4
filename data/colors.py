#
#  Nomitron 4 Safe
#

# Command
async def green(self, payload):
    pid = payload['Author ID']

    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |   Setting Color For ',player.name)
        
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Orange'])
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Purple'])
        await self.Refs['players'][pid].add_roles(   self.Refs['roles']['Green'])
        self.Data['PlayerData'][pid]['Color'] = {'Hue':"Green", "time": self.now() + self.day}

    elif self.now() -  self.Data['PlayerData'][pid]['Color']['time'] > self.second and \
        self.Data['PlayerData'][pid]['Color']['Hue'] != "Purple" and \
        payload['Channel'] == 'actions':
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Orange'])
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Purple'])
        await self.Refs['players'][pid].add_roles(   self.Refs['roles']['Green'])
        self.Data['PlayerData'][pid]['Color'] = {'Hue':"Green", "time": self.now() + self.day}
    else:
        await payload['raw'].channel.send('-  You cannot be set to this color at this time.')

# Command
async def orange(self, payload,):
    pid = payload['Author ID']

    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |   Setting Color For ',player.name)
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Green'])
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Purple'])
        await self.Refs['players'][pid].add_roles(   self.Refs['roles']['Orange'])
        self.Data['PlayerData'][pid]['Color'] = {'Hue':"Orange", "time": self.now() + self.day}

    elif self.now() -  self.Data['PlayerData'][pid]['Color']['time'] > self.second  and \
        self.Data['PlayerData'][pid]['Color']['Hue'] != "Green" and \
        payload['Channel'] == 'actions':
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Green'])
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Purple'])
        await self.Refs['players'][pid].add_roles(   self.Refs['roles']['Orange'])

        self.Data['PlayerData'][pid]['Color'] = {'Hue':"Orange", "time": self.now() + self.day}
    else:
        await payload['raw'].channel.send('-  You cannot be set to this color at this time.')

# Command
async def purple(self, payload):
    pid = payload['Author ID']

    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |  Setting Color For ',player.name)
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Orange'])
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Green'])
        await self.Refs['players'][pid].add_roles(   self.Refs['roles']['Purple'])
        self.Data['PlayerData'][pid]['Color'] = {'Hue':"Purple", "time": self.now() + self.day}

    elif self.now() -  self.Data['PlayerData'][pid]['Color']['time'] > self.second  and \
        self.Data['PlayerData'][pid]['Color']['Hue'] != "Orange" and \
        payload['Channel'] == 'actions':
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Orange'])
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Green'])
        await self.Refs['players'][pid].add_roles(   self.Refs['roles']['Purple'])
        self.Data['PlayerData'][pid]['Color'] = {'Hue':"Purple", "time": self.now() + self.day}
    else:
        await payload['raw'].channel.send('-  You cannot be set to this color at this time.')
