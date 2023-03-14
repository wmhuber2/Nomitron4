import random
# command
async def removeBuds(self, payload):
    print('   |   Removing Buds')
    self.Data['Buddies'] ={ 'Buddies' : []}
    await buddify(self)

# function
async def tally_buds(self):
    print('   |   Making Buds!')
    for bud in self.Data['Buddies']['Buddies']:
        basePID = bud[0]
        baseIsGreen  = self.Refs['players'][basePID].get_role(self.Refs['roles']['Green'].id) 
        baseIsOrange = self.Refs['players'][basePID].get_role(self.Refs['roles']['Orange'].id) 
        baseIsPurple = self.Refs['players'][basePID].get_role(self.Refs['roles']['Purple'].id) 

        allSame = True
        for pid in bud:
            isGreen  = self.Refs['players'][pid].get_role(self.Refs['roles']['Green'].id) 
            isOrange = self.Refs['players'][pid].get_role(self.Refs['roles']['Orange'].id) 
            isPurple = self.Refs['players'][pid].get_role(self.Refs['roles']['Purple'].id) 

            if isGreen == baseIsGreen and isOrange == baseIsOrange and isPurple == baseIsPurple: pass
            else: allSame = False
        if allSame:
            for b in bud: 
                self.Data['PlayerData'][b]['Friendship Tokens'] += 1
                self.Tasks.add( self.Mods.suitsRule.rewardMethod(self, b, 'Buddy') )

# Weekly Schedule
async def buddify(self):
    await tally_buds(self)
    validBuddies = []
    for pid in self.Data['PlayerData'].keys():
        isInactive = self.Refs['players'][pid].get_role(self.Refs['roles']['Inactive'].id) is not None
        if not isInactive: validBuddies.append(pid)
        else: print('   |   ', self.Data['PlayerData'][pid]['Name'], 'is inactive bud')
    
    print('   |   Bud Len:', len(validBuddies))
    newBuddies = []
    while len(validBuddies) >= 2:
        bud1 = random.choice(validBuddies)
        validBuddies.remove(bud1)

        bud2 = random.choice(validBuddies)
        validBuddies.remove(bud2)

        newBuddies.append([bud1,bud2])

    if len(validBuddies) == 1 and len(self.Data['Buddies']['Buddies']) > 0:
        newBuddies[-1].append(validBuddies[0])

    if len(newBuddies) > 0:
        cont = "This Week's Buddies Are:"
        for bud in newBuddies:
            cont += "\n - " 
            for b in bud: cont += f"<@{b}>, "
        await self.Refs['channels']['actions'].send(f"-  {cont}")
    else: 
        await self.Refs['channels']['actions'].send('-  Not enough players for buddies')
    self.Tasks.update(set([
        setbuddies(self, newBuddies)
    ]))

    
# function
async def setbuddies(self, newBuddies):
    self.Data['Buddies']['Buddies'] = newBuddies