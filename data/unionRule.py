async def unionize(self, payload):
    ActivePlayers = [] 
    for player in self.Refs['roles']['Player'].members:
        if player not in self.Refs['roles']['Inactive'].members:
            ActivePlayers.append(player.id)
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

    for pid in union1:
        await self.Refs['players'][p].add_roles(   self.Refs['roles']['Union 1']) 
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 2']) 
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 3']) 
    
    for pid in union2:
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 1']) 
        await self.Refs['players'][p].add_roles(   self.Refs['roles']['Union 2']) 
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 3']) 
    
    for pid in union3:
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 1']) 
        await self.Refs['players'][p].remove_roles(self.Refs['roles']['Union 2']) 
        await self.Refs['players'][p].add_roles(   self.Refs['roles']['Union 3']) 

    msg = "New Unions Formed: \n" \
          "Union 1: "+ ' '.join([self.Refs['players'][p].mention for i in union1])+"\n" \
          "Union 2: "+ ' '.join([self.Refs['players'][p].mention for i in union2])+"\n" \
          "Union 3: "+ ' '.join([self.Refs['players'][p].mention for i in union3])+"\n" 
    await self.Refs['channels']['actions'].send(msg)

