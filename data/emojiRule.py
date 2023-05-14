#
#  Nomitron 4 Safe
#


# Command 
async def toggleEmoji(self, payload):
    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) == 3: 
        _, playerid, emoji = payload['Content'].split(' ')
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |  Toggleing Emoji For',player.name, [hex(ord(i)) for i in emoji])

        await payload['raw'].add_reaction('✔️')
        if emoji not in self.Data['PlayerData'][pid]['Emojis']:
            await addEmoji(self, pid, emoji)
        elif emoji in self.Data['PlayerData'][pid]['Emojis']:
            await removeEmoji(self, pid, emoji)

async def update(self):
    await updateEmojis(self)

# Command
async def nick(self, payload):
    print('   |  Setting Nick')

    if self.Data['PlayerData'][payload['Author ID']].get('Union State') == 'Break':
        await payload['raw'].add_reaction('❌')
        return

    self.Data['PlayerData'][payload['Author ID']]['Nick'] = payload['Content'][6:]
    await payload['raw'].add_reaction('✔️')
    await updateEmojis(self)

# Function
async def updateEmojis(self):
    #print('   |  Updating Emojis')
    for pid in self.Data['PlayerData'].keys():
        player = self.Refs['players'][pid]
        emojis = ''.join(sorted(self.Data['PlayerData'][pid]['Emojis'])).replace(' ','')
        
        nickname = self.Data['PlayerData'][pid]['Nick'] + emojis
        nickname = nickname.replace('\uFE0F','').replace('\uFE0E','')
        old_nick = player.nick
        if old_nick == None: old_nick = player.name
        if nickname != old_nick:
            if self.admin == pid:    pass #await self.dm(pid,f"As admin, you must set your nick to {nickname}")
            else:                       
                print('   |  Nick:', old_nick,'->', nickname )
                await player.edit(nick = nickname)

# Function
async def removeEmoji(self, pid, emoji):
    if emoji in self.Data['PlayerData'][pid]['Emojis']:
        try: 
            self.Data['PlayerData'][pid]['Emojis'].remove( emoji )
            await updateEmojis(self)
        except ValueError: pass

# Function
async def addEmoji(self, pid, emoji):
    if emoji not in self.Data['PlayerData'][pid]['Emojis']:
        self.Data['PlayerData'][pid]['Emojis'].append( emoji )
        await updateEmojis(self)