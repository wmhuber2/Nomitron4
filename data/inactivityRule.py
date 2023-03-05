
async def makeActive(self,pid):
        await self.Refs['channels']['actions'].send("-  "+self.Data['PlayerData'][pid]['Name']+" Is Now Active")
        await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Inactive'])
        self.Data['PlayerData'][pid]['Inactive'] = None    

async def makeInactive(self,pid, reason = None):
        await self.Refs['channels']['actions'].send("-  "+self.Data['PlayerData'][pid]['Name']+" Is Now Inactive")
        await self.Refs['players'][pid].add_roles(self.Refs['roles']['Inactive'])
        self.Data['PlayerData'][pid]['Inactive'] = reason    



async def attemptActivate(self,pid):
    isInactive = self.Refs['players'][pid].get_role(self.Refs['roles']['Inactive'].id) is not None

    if isInactive and self.Data['PlayerData'][pid]['Inactive'] is None:
        await makeActive(self, pid)
    
    if isInactive and self.Data['PlayerData'][pid]['Inactive'] != "315":    
        await makeActive(self, pid)

async def activateOnEndorse(self, pid):
    isInactive = self.Refs['players'][pid].get_role(self.Refs['roles']['Inactive'].id) is not None
    if isInactive and self.Data['PlayerData'][pid]['Inactive'] in [None,'','315']:    await makeActive(self, pid)

async def activeOnVote(self, pid):
    isInactive = self.Refs['players'][pid].get_role(self.Refs['roles']['Inactive'].id) is not None
    
    if isInactive and self.Data['PlayerData'][pid]['Inactive'] is None:
        await makeActive(self, pid)
            
    if isInactive and self.Data['PlayerData'][pid]['Inactive'] == "315":
        await self.Refs['players'][pid].send( content = "You must endorse a proposal to become active again. (Rule 315)")


# command
async def togglePermInactive(self, payload):
    if payload.get('Author') not in self.moderators: return 

    reason = "Mods"
    playerid = payload['Content'].split(' ')[1]
    if len(payload['Content'].split(' ')) > 2:
        reason = ' '.join(payload['Content'].split(' ')[2:])
    player = await self.getPlayer(playerid, payload)
    pid = player.id

    isInactive = self.Refs['players'][pid].get_role(self.Refs['roles']['Inactive'].id) is not None

    if isInactive: await makeActive(self, pid)
    else: await makeInactive(self, pid, reason)

async def update(self):
    endorsingPlayers = set()
    for pid in self.Data['PlayerData'].keys():
        endorsingPlayers.update(self.Data['PlayerData'][pid]['Proposal']['Supporters'])
            
    for player in self.Data['PlayerData'].keys():
        isInactive = self.Refs['players'][player].get_role(self.Refs['roles']['Inactive'].id) is not None
        willBeInactive = self.Data['PlayerData'][player].get('Will Become Inactivie At')


        if player not in endorsingPlayers and willBeInactive is None and not isInactive:
            print(f'   |   - Making {player} inactive')
            self.Data['PlayerData'][player]['Will Become Inactivie At'] = self.Data['Time'] + self.hour*36
            await self.dm(pid,"You will be Inactive in 36 hrs because you are not endorsing any proposals. Endorse a proposal or create one to become active again. (Rule 315)")
        
        elif player not in endorsingPlayers and willBeInactive is not None and willBeInactive < self.Data['Time']:
            await makeInactive(self,player,"315")
            self.Data['PlayerData'][player]['Will Become Inactivie At'] = None

        elif isInactive and self.Data['PlayerData'][player]['Inactive'] == "315" and player in endorsingPlayers:
            print(f'   |   - Making {player} active')
            self.Data['PlayerData'][player]['Will Become Inactivie At'] = None
            await makeActive(self,player)

       