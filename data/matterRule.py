

async def cake(self,payload):
    self.Data['PlayerData'][payload['Author ID']]['Matter Vote'] = 'Cake'
    await payload['raw'].add_reaction('✔️')
async def sandwich(self,payload):
    self.Data['PlayerData'][payload['Author ID']]['Matter Vote'] = 'Sandwich'
    await payload['raw'].add_reaction('✔️')
async def salad(self,payload):
    self.Data['PlayerData'][payload['Author ID']]['Matter Vote'] = 'Salad'
    await payload['raw'].add_reaction('✔️')

async def tallyMatter(self, payload = None):
    cake, sandwich, salad = [],[],[]
    for pid in self.Data['PlayerData'].keys():
        if self.Data['PlayerData'][pid].get('Matter Vote') == 'Cake':      cake.append(pid)
        if self.Data['PlayerData'][pid].get('Matter Vote') == 'Sandwich':  sandwich.append(pid)
        if self.Data['PlayerData'][pid].get('Matter Vote') == 'Salad':     salad.append(pid)
        self.Data['PlayerData'][pid]['Matter Vote'] = None
    if len(cake) == len(sandwich) and len(sandwich) == len(salad):
        msg = await self.Refs['channels']['actions'].send("- Tie in Matter Baby. Proposer, cast your tiebreaker vote or abstain. (Mods will react)")
        if self.Data['PlayerData'].get('Old Matter Votes') is None:
            self.Data['Old Matter Votes'] = {}
        await msg.add_reaction('🥪')
        await msg.add_reaction('🍰')
        await msg.add_reaction('🥗')
        await msg.add_reaction('🇦')
        self.Data['Old Matter Votes'][msg.id] = {
            'sandwich'  : sandwich,
            'salad'     : salad,
            'cake'      : cake,
            'tie'       : cake + salad + sandwich
        }

    elif len(cake) > len(sandwich) and len(cake) > len(salad):
        await self.Refs['channels']['actions'].send("- Matter Baby Winner is CAKE")
        for pid in cake: 
            self.Tasks.add( self.Mods.emojiRule.addEmoji(self, pid, '🧠' ) )
    elif len(sandwich) > len(cake) and len(sandwich) > len(salad):
        await self.Refs['channels']['actions'].send("- Matter Baby Winner is SANDWICH")
        for pid in sandwich: 
            self.Tasks.add( self.Mods.emojiRule.addEmoji(self, pid, '🧠' ) )
    elif len(salad) > len(sandwich) and len(salad) > len(cake):
        await self.Refs['channels']['actions'].send("- Matter Baby Winner is SALAD")
        for pid in salad: 
            self.Tasks.add( self.Mods.emojiRule.addEmoji(self, pid, '🧠' ) )

    elif len(cake) == len(sandwich):
        await self.Refs['channels']['actions'].send("- Matter Baby Winners are CAKE + SANDWICH")
        for pid in sandwich: 
            self.Tasks.add( self.Mods.tokensRule.addTokens(self, pid, 1) )
        for pid in cake: 
            self.Tasks.add( self.Mods.emojiRule.addEmoji(self, pid, '🧠' ) )
    elif len(sandwich) == len(salad):
        await self.Refs['channels']['actions'].send("- Matter Baby Winners are SALAD + SANDWICH")
        for pid in sandwich: 
            self.Tasks.add( self.Mods.tokensRule.addTokens(self, pid, 1) )
        for pid in salad: 
            self.Tasks.add( self.Mods.emojiRule.addEmoji(self, pid, '🧠' ) )
    elif len(salad) == len(cake):
        msg = await self.Refs['channels']['actions'].send("- Tie in Matter Baby. Proposer, cast your tiebreaker vote or abstain. (Mods will react)")
        if self.Data['PlayerData'].get('Old Matter Votes') is None:
            self.Data['Old Matter Votes'] = {}
        await msg.add_reaction('🍰')
        await msg.add_reaction('🥗')
        await msg.add_reaction('🇦')
        self.Data['Old Matter Votes'][msg.id] = {
            'sandwich'  : sandwich,
            'salad'     : salad,
            'cake'      : cake,
            'tie'       : salad + cake
        }
        
async def on_reaction(self, payload):
    if payload['name'] in self.moderators and payload['msg'].author.id == self.clientid:
        if payload['msg'].id not in self.Data['Old Matter Votes']: return
        if payload['emoji'] == '🥪':
            for pid in self.Data['Old Matter Votes'][payload['msg'].id]['sandwich']: 
                self.Tasks.add( self.Mods.emojiRule.addEmoji(self, pid, '🧠' ) )
        elif payload['emoji'] == '🍰': 
            for pid in self.Data['Old Matter Votes'][payload['msg'].id]['cake']: 
                self.Tasks.add( self.Mods.emojiRule.addEmoji(self, pid, '🧠' ) )
        elif payload['emoji'] == '🥗':
            for pid in self.Data['Old Matter Votes'][payload['msg'].id]['salad']: 
                self.Tasks.add( self.Mods.emojiRule.addEmoji(self, pid, '🧠' ) )
        elif payload['emoji'] == '🇦':            
            for pid in self.Data['Old Matter Votes'][payload['msg'].id]['tie']: 
                self.Tasks.add( self.Mods.tokensRule.addTokens(self, pid, -1) )
        else: return

        del self.Data['Old Matter Votes'][payload['msg'].id]
        await self.Refs['channels']['actions'].send("- Tie in Matter Baby Resolved. ")
        
