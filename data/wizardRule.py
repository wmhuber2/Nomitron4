import time
"""
Function Called on Reaction
"""
async def on_reaction(self, payload):
    if payload['msg'].id == self.Data['Wizard']['MSG']:
        Data['Wizard']['MSG'] = None
        
        basePID = payload['user'].id
        baseIsGreen  = self.Refs['players'][basePID].get_role(self.Refs['roles']['Green'].id) 
        baseIsOrange = self.Refs['players'][basePID].get_role(self.Refs['roles']['Orange'].id) 
        baseIsPurple = self.Refs['players'][basePID].get_role(self.Refs['roles']['Purple'].id) 

        for pid in  self.Data['PlayerData'].keys():
            isGreen  = self.Refs['players'][pid].get_role(self.Refs['roles']['Green'].id) 
            isOrange = self.Refs['players'][pid].get_role(self.Refs['roles']['Orange'].id) 
            isPurple = self.Refs['players'][pid].get_role(self.Refs['roles']['Purple'].id) 

            if isGreen == baseIsGreen and isOrange == baseIsOrange and isPurple == baseIsPurple: 
                await self.Mods.emojiRule.addEmoji(pid, '🧙' )

"""
Update Function Called Every 10 Seconds
"""
async def update(self):
    if self.now().hour - self.Data['Wizard']['Time'].hour >= 1 and False:
        self.Data['Wizard']['Time'] = self.now().hour
        if int(np.random.random()*100) == 0 :
            self.Data['Wizard']['Time'] = self.now().hour
            msg  = await self.Refs['channels']['game'].send('GOLDEN SNITCH')
            self.Data['Wizard']['MSG'] = msg.id
            for pid in self.Data['PlayerData'].keys():
                await self.Mods.emojiRule.removeEmoji(pid, '🧙' )

