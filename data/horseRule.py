import random

async def neigh(self, payload):
    if payload['Channel'] != 'Actions':
        if payload['Author ID'] in self.Data['Horse']['Opted In']:
            await payload['raw'].channel.send('-  You already opted in, but I like your enthusiasm')
        else:
            self.Data['Horse']['Opted In'].append( payload['Author ID'] )
            await payload['raw'].channel.send('-  You are opted in to the Horse Newsletter')

async def ihatefun(self,payload):
    if payload['Channel'] != 'Actions':
        if payload['Author ID'] not in self.Data['Horse']['Opted In']:
            await payload['raw'].channel.send('You already opted out.')
        else:
            self.Data['Horse']['Opted In'].remove( payload['Author ID'] )
            await payload['raw'].channel.send('You are opted out of the Horse Newsletter.')

async def randHorse(self, payload = None):
    images = [
        "https://media.giphy.com/media/JnvlBMZ5R0GyI/giphy.gif",
        "https://media.giphy.com/media/JnvlBMZ5R0GyI/giphy.gif",
        "https://media.giphy.com/media/dBmTd7FBuQNLeRfo4B/giphy.gif"]
    
    msg = random.choice(images) + '\n'
    for optin in self.Data['Horse']['Opted In']:
        msg += f'<@{optin}> '
    await self.Refs['channels']['off-topic'].send(msg)

horses = {
'Icelandic Horse': 14,
'Norwegian Fjord': 13,
'Akhal-Teke': 16,
'Mongolian Horse': 12,
'Arabian Horse': 15,
'Caspian Horse': 9,
'Turkoman Horse': 16,
'Przewalski’s Horse': 12,
}

async def giveRandHorse(self, payload):
    pid = payload['Author ID']
    if payload.get('Author') not in self.moderators : return

    if len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |   Setting Horse For ',player.name)
        self.Data['PlayerData'][pid]['Horse'] = {
            'Type':random.choice(list(horses.keys())), 
            'Has Been Soothed': False,
            'Has Been Feed': False,
            'Is Friend':False,
            'Is Dead': False
        }

        self.Data['PlayerData'][pid]['Horse']['Health']     = horses[self.Data['PlayerData'][pid]['Horse']['Type']]
        self.Data['PlayerData'][pid]['Horse']['Spookiness'] = horses[self.Data['PlayerData'][pid]['Horse']['Type']]

    else:
        for pid in self.Data['PlayerData']:
            print('   |   Setting Horse For ',self.Data['PlayerData'][pid]['Name'])
            self.Data['PlayerData'][pid]['Horse'] = {
                'Type':random.choice(list(horses.keys())), 
                'Has Been Soothed': False,
                'Has Been Feed': False,
                'Is Friend':False,  
                'Is Dead': False
            }
            self.Data['PlayerData'][pid]['Horse']['Health']     = horses[self.Data['PlayerData'][pid]['Horse']['Type']]
            self.Data['PlayerData'][pid]['Horse']['Spookiness'] = horses[self.Data['PlayerData'][pid]['Horse']['Type']]

async def feed(self, payload):
    pid = payload['Author ID']
    self.Data['PlayerData'][pid]['Horse']['Has Been Feed'] = True
    await payload['raw'].add_reaction('✔️')

async def soothe(self, payload):
    pid = payload['Author ID']
    self.Data['PlayerData'][pid]['Horse']['Has Been Soothed'] = True
    self.Data['PlayerData'][pid]['Horse']['Spookiness']      -= 1
    await payload['raw'].add_reaction('✔️')

async def sugar(self, payload):
    pid = payload['Author ID']
    try: offering = int(payload['Content'].split(' ')[1])
    except Exception as e: 
        print(e)
        await payload['raw'].channel.send("-  I couldnt understand your command")
        return

    if self.Data['PlayerData'][payload['Author ID']]['Friendship Tokens'] - offering*2 < 0: 
        await payload['raw'].channel.send("-  You are too poor.")
        return

    if offering >= horses[self.Data['PlayerData'][pid]['Horse']['Type']]:
        await payload['raw'].channel.send("Overfeeding a horse is a crime. >:(")
        return
    
    await self.Mods.tokensRule.addTokens(self, payload['Author ID'], -offering*2)
    self.Data['PlayerData'][pid]['Horse']['Health'] += offering
    await payload['raw'].add_reaction('✔️')


async def checkHorses(self, payload= None):
    if payload.get('Author') not in self.moderators : return
    for pid in self.Data['PlayerData'].keys():
        if not self.Data['PlayerData'][pid]['Horse']['Has Been Soothed']:
            self.Data['PlayerData'][pid]['Horse']['Spookiness'] = horses[self.Data['PlayerData'][pid]['Horse']['Type']]
        self.Data['PlayerData'][pid]['Horse']['Has Been Soothed'] = False


        if not self.Data['PlayerData'][pid]['Horse']['Has Been Feed']:
            self.Data['PlayerData'][pid]['Horse']['Health'] -= 1
        self.Data['PlayerData'][pid]['Horse']['Has Been Feed'] = False

        if self.Data['PlayerData'][pid]['Horse']['Health'] == 0 and not self.Data['PlayerData'][pid]['Horse']['Is Dead'] :
            await self.Refs['channels']['actions'].send(f'<@{pid}> has killed their horse through neglect.')
            self.Data['PlayerData'][pid]['Horse']['Is Dead'] = True
            await self.Mods.emojiRule.removeEmoji(self, pid, '🐴' )


        if self.Data['PlayerData'][pid]['Horse']['Spookiness'] == 0 and self.Data['PlayerData'][pid]['Horse']['Health'] > 0:
            self.Data['PlayerData'][pid]['Horse']['Is Friend']= True  
            await self.Mods.emojiRule.addEmoji(self, pid, '🐴' )