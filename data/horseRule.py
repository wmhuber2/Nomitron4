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