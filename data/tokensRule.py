#
#  Nomitron 4 Safe
#

# Command
async def setTokens(self, payload):
    if payload.get('Author') not in self.moderators: return
    
    cont = payload['Content'].strip().split(' ')
    if len(cont) == 3 : 
        print('   |   Setting Tokens')
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id

        toset = 0
        try: toset = int(cont[2])
        except ValueError: return
        print("   |  ", toset)
        self.Data['PlayerData'][pid]['Friendship Tokens'] = toset
        
# Command
async def give(self, payload):
    playerid = payload['Content'].split(' ')[1]
    player = await self.getPlayer(playerid, payload)
    pid = player.id

    if self.Data['PlayerData'][payload['Author ID']]['Friendship Tokens'] <= 0: 
        await payload['raw'].add_reaction('❌')
        return

    self.Data['PlayerData'][pid]['Friendship Tokens'] += 1
    self.Data['PlayerData'][payload['Author ID']]['Friendship Tokens'] -= 1

async def addTokens(self, pid, n):
    self.Data['PlayerData'][pid]['Friendship Tokens'] += n
