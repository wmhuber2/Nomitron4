import random, numpy

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
        "https://media.giphy.com/media/dBmTd7FBuQNLeRfo4B/giphy.gif",
        "https://media.giphy.com/media/uA2ZclTgLaaoE/giphy.gif",
        "https://media.giphy.com/media/ByTh8UTOcOXL2/giphy.gif",
        "https://media.giphy.com/media/l4pTkyF1QfRIpjPVK/giphy.gif",
        "https://media.giphy.com/media/2YpSDVERqyhJmcG5cA/giphy-downsized-large.gif",
        "https://media.giphy.com/media/3Rbfli2Rl9SVI4WScv/giphy.gif",
        "https://media.giphy.com/media/sRclnIVXVvz44/giphy.gif",
    ]
    
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

    cont = payload['Content'].strip().split(' ')
    if payload.get('Author') in self.moderators and len(cont) == 3 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id

        toset = 0
        try: toset = int(cont[2])
        except ValueError: return
        self.Data['PlayerData'][pid]['Horse']['Spookiness'] = toset
        print('   |   Setting soothe counter For ',player.name)
        print("   |  ", toset)
        await payload['raw'].add_reaction('✔️')

    elif not self.Data['PlayerData'][pid]['Horse']['Has Been Soothed']:
        self.Data['PlayerData'][pid]['Horse']['Has Been Soothed'] = True
        self.Data['PlayerData'][pid]['Horse']['Spookiness']      -= 1
        if pid in self.Data['Horse']['Racers']:
            self.Data['PlayerData'][pid]['Horse']['Race Soothe Bonus'] = 1
        await payload['raw'].add_reaction('✔️')

async def setHorseHealth(self, payload):
    pid = payload['Author ID']

    cont = payload['Content'].strip().split(' ')
    if payload.get('Author') in self.moderators and len(cont) == 3 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id

        toset = 0
        try: toset = int(cont[2])
        except ValueError: return
        self.Data['PlayerData'][pid]['Horse']['Health'] = toset
        print('   |   Setting health counter For ',player.name)
        print("   |  ", toset)
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

async def spookinessCheck(self):
    for pid in self.Data['PlayerData'].keys():
        if not self.Data['PlayerData'][pid]['Horse']['Has Been Soothed']:
            self.Data['PlayerData'][pid]['Horse']['Spookiness'] = horses[self.Data['PlayerData'][pid]['Horse']['Type']]
        self.Data['PlayerData'][pid]['Horse']['Has Been Soothed'] = False

async def checkHorses(self, payload= None):
    if payload is not None and payload.get('Author') not in self.moderators : return
    for pid in self.Data['PlayerData'].keys():
        if self.Data['PlayerData'][pid].get('Horse') is None: continue


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

async def horsename(self, payload):
    pid = payload['Author ID']
    cmd = payload['Content'].split(' ')
    if len(cmd) < 1:
        await payload['raw'].channel.send("You must give it a name")
        return
    name = ' '.join(cmd[1:])
    self.Data['PlayerData'][pid]['Horse']['Name'] = name
    self.Data['PlayerData'][pid]['Horse']['Victories'] = 0
    self.Data['PlayerData'][pid]['Horse']['Stars'] = ''
    await payload['raw'].add_reaction('✔️')

async def chooseRaceHorses(self, payload = None):
    if payload is not None and payload.get('Author') not in self.moderators : return

    raceHorses = []

    for pid in self.Data['PlayerData'].keys():
        if self.Data['PlayerData'][pid]['Horse'].get('Name') is None: continue
        if self.Data['PlayerData'][pid]['Horse'].get('Has Raced') == True: 
            self.Data['PlayerData'][pid]['Horse']['Has Raced'] = False
            continue
        raceHorses.append(pid)

    msg = ''
    if len(raceHorses) < 3:
        msg = "There are not enough horses to race. *Sad Horse Noises*"
        raceHorses = []
    else: 
        raceHorses  = numpy.random.choice(raceHorses, size=3, replace=False).tolist()
        msg = "This week's race horses are!"
    sootheBonus = [0,0,0]
    for pid in self.Data['PlayerData'].keys():
        if pid in raceHorses:
            msg += "\n- "+self.Data['PlayerData'][pid]['Name']+'\'s Horse: '+self.Data['PlayerData'][pid]['Horse']['Name']
            self.Data['PlayerData'][pid]['Horse']['Race Bonus'] = \
                int(self.Data['PlayerData'][pid]['Horse']['Has Been Soothed'])
            self.Data['PlayerData'][pid]['Horse']['Betters'] = []
        else:
            self.Data['PlayerData'][pid]['Horse']['Race Soothe Bonus'] = None
    self.Data['Horse']['Racers'] = raceHorses
    if self.Data['Horse'].get('Bet Pool') is None: self.Data['Horse']['Bet Pool'] = 0

    await self.Refs['channels']['actions'].send(msg)

async def raceHorses(self,payload = None):
    scores = numpy.random.randint(1, 21, 3)

    if len(self.Data['Horse']['Racers']) != 3:
        await self.Refs['channels']['actions'].send("There are not enough horses to race. *Sad Horse Noises*")
        return

    for i in [0,1,2]:
        pid = self.Data['Horse']['Racers'][i]

        healthDif = horses[self.Data['PlayerData'][pid]['Horse']['Type']] - self.Data['PlayerData'][pid]['Horse']['Health']
        scores[i] -= healthDif

        if self.Data['PlayerData'][pid]['Horse']['Is Friend']:   scores[i] += 3

        scores[i] += self.Data['PlayerData'][pid]['Horse']['Race Soothe Bonus'] in [1, True]
    
    sortedScores = sorted(set(scores))
    score1st = []
    score2st = [] 
    score3st = []

    for i in [0,1,2]:
        pid = self.Data['Horse']['Racers'][i]
        if len(sortedScores) >= 1 and scores[i] == sortedScores[0]: score1st.append(pid)
        if len(sortedScores) >= 2 and scores[i] == sortedScores[1]: score2st.append(pid)
        if len(sortedScores) >= 3 and scores[i] == sortedScores[2]: score3st.append(pid)


    msg = "Race Results In:" 
    msg += f"\n - 1st ({sortedScores[0]}): "
    for pid in score1st:
        betReward    = self.Data['Horse']['Bet Pool'] // len(self.Data['PlayerData'][pid]['Horse']['Betters'])
        self.Data['Horse']['Bet Pool'] = self.Data['Horse']['Bet Pool'] % len(self.Data['PlayerData'][pid]['Horse']['Betters'])

        for betpid in self.Data['PlayerData'][pid]['Horse']['Betters']:
            self.Tasks.add( self.Mods.tokensRule.addTokens(self, betpid, betReward) )
        del self.Data['PlayerData'][pid]['Horse']['Betters']

        msg += '\n    ' + self.Data['PlayerData'][pid]['Name']+'\'s Horse: '+self.Data['PlayerData'][pid]['Horse']['Name']
        self.Data['PlayerData'][pid]['Horse']['Stars']  += '⭐'
        self.Data['PlayerData'][pid]['Horse']['Victories'] += 1

        if self.Data['PlayerData'][pid]['Horse']['Victories'] == 10:
            toDo.append( self.Mods.emojiRule.addEmoji(self,pid, '🏆') )
            self.Data['PlayerData'][pid]['Horse']['Name'] += '🏆'

    if len(score2st) > 0:
        msg += f"\n - 2st ({sortedScores[1]}): "
        for pid in score2st:
            msg += '\n    ' + self.Data['PlayerData'][pid]['Name']+'\'s Horse: '+self.Data['PlayerData'][pid]['Horse']['Name']
            self.Data['PlayerData'][pid]['Horse']['Victories'] = 0

            del self.Data['PlayerData'][pid]['Horse']['Betters']

    if len(score3st) > 0:
        msg += f"\n - 3st ({sortedScores[2]}): "
        for pid in score3st:
            msg += '\n    ' + self.Data['PlayerData'][pid]['Name']+'\'s Horse: '+self.Data['PlayerData'][pid]['Horse']['Name']
            self.Data['PlayerData'][pid]['Horse']['Victories'] = 0

            del self.Data['PlayerData'][pid]['Horse']['Betters']

    
    await self.Refs['channels']['actions'].send(msg)

async def bet(self, payload):
    pid = payload['Author ID']
    cmd = payload['Content'].split(' ')
    if len(cmd) < 1:
        await payload['raw'].channel.send("You must enter a name")
        return
    name = ' '.join(cmd[1:])

    if self.Data['PlayerData'][payload['Author ID']]['Friendship Tokens'] - 2 < 0: 
        await payload['raw'].channel.send("-  You are too poor.")
        return

    for racerpid in self.Data['Horse']['Racers']:
        if name == self.Data['PlayerData'][racerpid]['Horse']['Name']:
            if self.Data['PlayerData'].get('Horses You Bet On') is None:
                self.Data['PlayerData']['Horses You Bet On'] = []
            if racerpid in self.Data['PlayerData']['Horses You Bet On']:
                await payload['raw'].channel.send("You already bet on this horse.")
                return

            if self.Data['PlayerData'][racerpid]['Horse'].get('Betters') is None:
                await payload['raw'].channel.send("This Horse Is Not in a Race")
                return
            else:
                self.Data['PlayerData'][racerpid]['Horse']['Betters'].append(pid)
                self.Data['Horse']['Bet Pool'] += 2
                self.Data['PlayerData'][payload['Author ID']]['Friendship Tokens'] -= 2
                self.Data['PlayerData']['Horses You Bet On'].append(racerpid)
                await payload['raw'].add_reaction('✔️')
                return
    
    await payload['raw'].channel.send("Could Not Find Horse. Is the name correct?")
    



