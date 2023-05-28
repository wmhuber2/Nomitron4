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

