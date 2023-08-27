import random
# command

# turnly
async def tubbify(self, payload):

    if payload is not None and payload.get('Author') not in self.moderators: return

    if self.Data.get('Tubby') is None: 
        self.Data['Tubby'] = {
            'Tinky-Winky': { 'emoji':'🟪', 'pid' : None },
            'Dipsy'      : { 'emoji':'🟩', 'pid' : None },
            'Laa-Laa'    : { 'emoji':'🟨', 'pid' : None },
            'Po'         : { 'emoji':'🟥', 'pid' : None },
        }

    tubbySteals = []
    playrSteals = []

    activeTubSteals = []
    activePlrSteals = []

    totalActTubs = []
    totalActPlrs = []

    cont = "Last Turn's Tubbys Were:\n"
    for tub in self.Data['Tubby'].keys():
        cont += f"- {tub} : <@{self.Data['Tubby'][tub]['pid']}> \n"
    await self.Refs['channels']['actions'].send(cont)

    for pid in self.Data['PlayerData'].keys():

        await self.Mods.emojiRule.removeEmoji(self, pid, '👀' )
        await self.Mods.emojiRule.removeEmoji(self, pid, '🌈' )
        await self.Mods.emojiRule.removeEmoji(self, pid, '🟪' )
        await self.Mods.emojiRule.removeEmoji(self, pid, '🟩' )
        await self.Mods.emojiRule.removeEmoji(self, pid, '🟨' )
        await self.Mods.emojiRule.removeEmoji(self, pid, '🟥' )

        isInactive = self.Refs['players'][pid].get_role(self.Refs['roles']['Inactive'].id) is not None
        isTub = False
        for tub in self.Data['Tubby'].keys():
            if pid == self.Data['Tubby'][tub]['pid']:
                if self.Data['PlayerData'][pid].get('Tubby Thief') not in [False, None]: tubbySteals.append(pid)
                if not isInactive:  totalActTubs.append(pid)
                isTub = True
                break
        if not isTub: 
            if self.Data['PlayerData'][pid].get('Tubby Thief') not in [False, None]: playrSteals.append(pid)
            if not isInactive:  totalActPlrs.append(pid)
    
    for pid in tubbySteals:
        if pid is None: continue
        await self.Mods.tokensRule.addTokens(self, pid, -min([len(tubbySteals), self.Data['PlayerData'][pid]['Friendship Tokens']]))
        if pid in totalActTubs: activeTubSteals.append(pid)
    for pid in playrSteals:
        await self.Mods.tokensRule.addTokens(self, pid, 1)
        if pid in totalActPlrs: activePlrSteals.append(pid)



    if None in totalActTubs: pass

    elif len(activeTubSteals) == 0            and len(activePlrSteals) == 0:
        await self.Refs['channels']['actions'].send("-  No Bonus Tubby Action.")


    elif len(activeTubSteals) == 0            and len(activePlrSteals) not in [0,len(totalActPlrs)] :
        for tub in self.Data['Tubby'].keys():
            if self.Data['Tubby'][tub]['pid'] is None: continue
            await self.Mods.tokensRule.addTokens(self, self.Data['Tubby'][tub]['pid'] , -1)
        await self.Refs['channels']['actions'].send("-  All Tubbies lose 1 Token.")


    elif len(activeTubSteals) == 0            and len(activePlrSteals) == len(totalActPlrs):
        for pid in tubbySteals+playrSteals:
            if pid is None: continue
            await self.Mods.emojiRule.addEmoji(self, pid, '👀' )
        await self.Refs['channels']['actions'].send("-  Bonus Emoji for all Thevies.")
        


    elif len(activeTubSteals) not in [0, 4]   and len(activePlrSteals) == 0:
        for pid in tubbySteals:
            if pid is None: continue
            await self.Mods.tokensRule.addTokens(self, pid,  min([len(tubbySteals), self.Data['PlayerData'][pid]['Friendship Tokens']]))
        await self.Refs['channels']['actions'].send("-  Tubby Theives Dont Loose Tokens.")


    elif len(activeTubSteals) not in [0, 4]   and len(activePlrSteals) not in [0,len(totalActPlrs)]:  
        await self.Refs['channels']['actions'].send("-  No Bonus Tubby Action.")


    elif len(activeTubSteals) not in [0, 4]   and len(activePlrSteals) == len(totalActPlrs):
        for pid in tubbySteals:
            if pid is None: continue
            await self.Mods.tokensRule.addTokens(self, pid, -1)
        
        await self.Refs['channels']['actions'].send("-  Tubbys loose 1 Token Extra .")
    
      

    elif len(activeTubSteals) == 4            and len(activePlrSteals) == 0:
        for tub in self.Data['Tubby'].keys():
            pid   = self.Data['Tubby'][tub]['pid']
            emoji = self.Data['Tubby'][tub]['emoji']

            if pid is None: continue

            await self.Mods.emojiRule.addEmoji(self, pid, emoji )
            await self.Mods.emojiRule.addEmoji(self, pid, '🌈' )
        
        await self.Refs['channels']['actions'].send("-  Bonus Emoji for Tubbies.")
       
    elif len(activeTubSteals) == 4            and len(activePlrSteals) not in [0,len(totalActPlrs)] :
        for pid in tubbySteals:
            if pid is None: continue
            await self.Mods.tokensRule.addTokens(self, pid,  min([len(tubbySteals), self.Data['PlayerData'][pid]['Friendship Tokens']]))
        await self.Refs['channels']['actions'].send("-  Tubby Theives Dont Loose Tokens.")
    
    elif len(activeTubSteals) == 4            and len(activePlrSteals) == len(totalActPlrs): 
        await self.Refs['channels']['actions'].send("-  No Bonus Tubby Action.")

  

    validTubbs = []
    for pid in self.Data['PlayerData'].keys():
        self.Data['PlayerData'][pid]['Tubby Thief'] = False
        isInactive = self.Refs['players'][pid].get_role(self.Refs['roles']['Inactive'].id) is not None
        if not isInactive: validTubbs.append(pid)
        else: print('   |   ', self.Data['PlayerData'][pid]['Name'], 'is inactive tub')
    
    print('   |   Tub Len:', len(validTubbs))
    if len(validTubbs) < 8:   validTubbs = [None,]*4
    random.shuffle(validTubbs)

    tubbies = {
        'Tinky-Winky': { 'emoji':'🟪', 'pid' : validTubbs[0] },
        'Dipsy'      : { 'emoji':'🟩', 'pid' : validTubbs[1] },
        'Laa-Laa'    : { 'emoji':'🟨', 'pid' : validTubbs[2] },
        'Po'         : { 'emoji':'🟥', 'pid' : validTubbs[3] },
    }

    if len(validTubbs) < 8: 
        await self.Refs['channels']['actions'].send('-  Not enough players for Tubbies')
 
    self.Tasks.add(self.set_data(['Tubby'], tubbies ) )
    

async def steal(self, payload):
    pid = payload['Author ID']
    self.Data['PlayerData'][pid]['Tubby Thief'] = True
    await payload['raw'].add_reaction('✔️')