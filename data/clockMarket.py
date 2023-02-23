import random
async def invest(self,payload):
    argv = payload['Content'].split(' ')
    pid = payload['Author ID']
    msg = payload['raw']
    amount = int(argv[1])
    
    if self.Data['PlayerData'][pid].get('ClockMarket') is None:
        self.Data['PlayerData'][pid]['ClockMarket'] = {
            'Invest Limit':5,
            'Ballance':0,
        }
    
    if   amount > self.Data['PlayerData'][pid]['ClockMarket']['Ballance']:
        await msg.channel.send("You cannot invest that amount this turn.")
    elif amount > self.Data['PlayerData'][pid]['Friendship Tokens']:
        await msg.channel.send("You do not have sufficient funds.")
    else:
        self.Data['PlayerData'][pid]['ClockMarket']['Ballance'] += amount
        self.Data['PlayerData'][pid]['Friendship Tokens'] -= amount
        await msg.add_reaction('✔️')
    
async def withdraw(self,payload):
    argv = payload['Content'].split(' ')
    pid = payload['Author ID']
    msg = payload['raw']
    if '.' in argv[1]:
        await msg.channel.send("You can only withdraw whole numbers of tokens.")
        return
    amount = int(argv[1])
    
    if self.Data['PlayerData'][pid].get('ClockMarket') is None:
        self.Data['PlayerData'][pid]['ClockMarket'] = {
            'Invest Limit':5,
            'Ballance':0,
        }
    
    if   amount > self.Data['PlayerData'][pid]['ClockMarket']['Ballance']:
        await msg.channel.send("You do not have that amount invested.")
    else:
        self.Data['PlayerData'][pid]['ClockMarket']['Ballance'] -= amount
        self.Data['PlayerData'][pid]['Friendship Tokens'] += amount

        self.Data['PlayerData'][pid]['ClockMarket']['Ballance'] = int(self.Data['PlayerData'][pid]['ClockMarket']['Ballance'])
        await msg.add_reaction('✔️')

# schedule
async def stonks(self):
    randNum = numpy.random.randint(0, 100, 1)
    multiplier = -1
    if   randNum < 52:
        multiplier = 1.2
        await self.Refs['channels']['actions'].send("- Financial News: Stocks on the RISE")
    elif randNum < 52+45:
        multiplier = 0.9
        await self.Refs['channels']['actions'].send("- Financial News: Stocks on the FALL")
    elif randNum < 52+45+2:        
        multiplier = 1.5
        await self.Refs['channels']['actions'].send("- Financial News: Stocks TO THE MOON")
    elif randNum < 52+45+2+1:
        multiplier = 0
        await self.Refs['channels']['actions'].send("- Financial News: I PULLED THE RUG ON YA!")
    
    for pid in self.Data['PlayerData'].keys():
        if self.Data['PlayerData'][pid].get('ClockMarket') is None:
            self.Data['PlayerData'][pid]['ClockMarket'] = {
                'Invest Limit':5,
                'Ballance':0,
            }
        if self.Data['PlayerData'][pid]['ClockMarket']['Ballance'] != 0
            self.Tasks.add( 
                self.set_data(['PlayerData',pid,'ClockMarket','Ballance'], 
                self.Data['PlayerData'][pid]['ClockMarket']['Ballance'] * multiplier)
            )