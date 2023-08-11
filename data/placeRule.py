#
#  Nomitron 4 Safe
#

import matplotlib.pyplot as plt
import numpy as np

# Command
colors = {
    'purple': [ 128, 0, 128], 
    'orange': [ 255, 168, 0],
    'green' : [ 0, 155, 0], 
    'red'   : [ 255, 0, 0], 
    'blue'  : [ 0, 0, 255], 
    'yellow': [ 255, 255, 0], 
    'black' : [ 0, 0, 0], 
    'white' : [ 255, 255, 255], 

}

async def newCanvas(self, payload):
    if payload.get('Author') in self.moderators:
        self.Data['Canvas'] = []
        for x in range(50):
            self.Data['Canvas'].append([])
            for y in range(50):
                self.Data['Canvas'][x].append([255,255,255, 0])

        await payload['raw'].channel.send('A new canvas is created!')
    else:
        await payload['raw'].add_reaction('❌')

async def resetPixelCounter(self, payload):
    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) == 2 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        self.Data['PlayerData'][pid]['Canvas Edits'] = 0
        await payload['raw'].add_reaction('✔️')

async def resetPixelCounterAll(self, payload = None):
    if payload is not None and payload.get('Author') not in self.moderators: return
    for pid in self.Data['PlayerData'].keys():
        self.Data['PlayerData'][pid]['Canvas Edits'] = 0

async def pixel(self, payload):
    pid   = payload['Author ID']

    if self.Data['PlayerData'][pid].get('Canvas Edits') is None:
        self.Data['PlayerData'][pid]['Canvas Edits'] = 0

    if len(payload['Content'].split(' ')) < 3 :
        await payload['raw'].channel.send('-  Format should be !pixel COLOR X-Y X-Y ...')
    cmd, color, *cords = payload['Content'].split(' ')
    print(cmd, color, cords)

    if self.Data['PlayerData'][pid].get('Union State') == 'Break':
        await payload['raw'].add_reaction('❌')
        return

    if payload['Channel'] != 'actions': return
    
    if self.Data['PlayerData'][pid]['Color']['Hue'] == "Purple" :
        if color not in ['purple', 'red', 'blue', 'black', 'white']:
            await payload['raw'].channel.send('-  You cannot set a pixel to this color.')
            return
    elif self.Data['PlayerData'][pid]['Color']['Hue'] == "Orange" :
        if color not in ['orange', 'red', 'yellow', 'black', 'white']:
            await payload['raw'].channel.send('-  You cannot set a pixel to this color.')
            return
    elif self.Data['PlayerData'][pid]['Color']['Hue'] == "Green" :
        if color not in ['green', 'yellow', 'blue', 'black', 'white']:
            await payload['raw'].channel.send('-  You cannot set a pixel to this color.')
            return
    else:
        if color not in ['black', 'white']:
            await payload['raw'].channel.send('-  You cannot set a pixel to this color.')
            return


    for c in cords:
        if ',' in c:
            x,y = c.split(',')
            try:
                x= int(x)
                y= int(y)
            except:
                await payload['raw'].channel.send(f'-  {c} is not formatted correctly.')
                continue

            if self.Data['PlayerData'][pid]['Canvas Edits'] == 24:
                await payload['raw'].channel.send(f'- You have run out of canvas edits. {c} and after has not been filled')
                break
            if x>50 or x<1 or y>50 or y<1:
                await payload['raw'].channel.send(f'-  {c} is out of range.')
            else:
                self.Data['Canvas'][y-1][x-1] = list(colors[color]) + [pid,]
                self.Data['PlayerData'][pid]['Canvas Edits'] += 1
        else:
            await payload['raw'].channel.send(f'-  {c} is not formatted correctly.')

    await payload['raw'].add_reaction('✔️')
    await plot(self)
                


async def fpixel(self, payload):
    if payload.get('Author') not in self.moderators: return

    playerid = payload['Content'].split(' ')[-1]
    player = await self.getPlayer(playerid, payload)
    if player is None: pid = 0
    else: pid = player.id

    if pid not in self.Data['PlayerData']: pid == 0

    if pid in self.Data['PlayerData'] and self.Data['PlayerData'][pid].get('Canvas Edits') is None:
        self.Data['PlayerData'][pid]['Canvas Edits'] = 0

    if len(payload['Content'].split(' ')) < 3 :
        await payload['raw'].channel.send('-  Format should be !pixel COLOR X-Y X-Y ...')
    cmd, color, *cords = payload['Content'].split(' ')[:-1]
    print(cmd, color, cords)

    for c in cords:
        if ',' in c:
            x,y = c.split(',')
            try:
                x= int(x)
                y= int(y)
            except:
                await payload['raw'].channel.send(f'-  {c} is not formatted correctly.')
                continue

            if x>50 or x<1 or y>50 or y<1:
                await payload['raw'].channel.send(f'-  {c} is out of range.')
            else:
                self.Data['Canvas'][y-1][x-1] = list(colors[color]) + [pid,]
        else:
            await payload['raw'].channel.send(f'-  {c} is not formatted correctly.')

    await payload['raw'].add_reaction('✔️')
    await plot(self)




async def plot(self):
    plt.figure(figsize=(6,6))
    plt.axis('off')
    plt.imshow(np.asarray(self.Data['Canvas'])[:,:,:3], vmax = 1, vmin =0, origin='lower', interpolation='nearest')
    plt.savefig('rplace.png',dpi = 100, bbox_inches='tight')
    plt.close()
    msg = await self.Refs['channels']['bot-spam'].send('r/Place Canvas', file=self.discord.File("rplace.png"))

    pidDict = {}
    for x in range(50):
        for y in range(50):
            if self.Data['Canvas'][x][y][3] == 0: continue

            if self.Data['Canvas'][x][y][3] not in pidDict:
                pidDict[self.Data['Canvas'][x][y][3]] = 0
            pidDict[self.Data['Canvas'][x][y][3]] += 1
    
    for pid in pidDict.keys():
        if pid not in self.Data['PlayerData'].keys(): continue
        if pidDict[pid] >= 25: await self.Mods.emojiRule.addEmoji(self, pid, '🎨' )
        else:                  await self.Mods.emojiRule.removeEmoji(self, pid, '🎨' )
    
    self.Data['Canvas-Image'] = msg.attachments[0].url
                
