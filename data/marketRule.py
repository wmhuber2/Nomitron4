#
#  Nomitron 4 Safe
#
import io
# Command
async def offer(self, payload):
    text = payload['Content'].split(' ')
    if payload['Channel'] != "market": return
    pid = payload['Author ID']
    offerd = 0


    if len(text) <= 3: 
        await self.dm(pid, "Your Offer Doesnt Have The Correct Format.")
        await payload['raw'].add_reaction('❌')
        return          

    try:   offerd = int(text[2])
    except ValueError: 
        await self.dm(pid, "Your Offer Doesnt Have The Correct Format.")
        await payload['raw'].add_reaction('❌')
        return          


    if offerd + self.Data['PlayerData'][pid]['Offers'] > self.Data['PlayerData'][pid]['Friendship Tokens']:
        await self.dm(pid, "You do not have enough Friendship Tokens to make that offer")
        await payload['raw'].add_reaction('❌')
        return
    
        
    await payload['raw'].add_reaction('✔️')
    self.Data['PlayerData'][pid]['Offers'] += offerd

# Function
async def acceptOffer(self, payload):
    offerd = 0
    text   = payload['message'].content[1:].split(' ')

    try:    offerd = int(text[2])
    except: return

    if '@' in payload['message'].content[1:].split(' ')[1] and f"{payload['user'].id}" != payload['message'].content[1:].split(' ')[2:-1]:
        print(f"{payload['user'].id}" , payload['message'].content[1:].split(' ')[1][2:-1])
        await self.dm(payload['user'].id, "You cannot accept that offer.")
        return
    
    files  = [self.discord.File(fp=io.StringIO(payload['message'].content), filename="Terms_Of_Offer.txt"),]
    await self.Refs['channels']['actions'].send(f"<@{payload['message'].author.id}>'s Offer Has Been Accepted By <@{payload['user'].id}> for {offerd} Tokens", files = files)
    await payload['message'].delete()

# Function
async def payOffer(self, payload):
    print('   |   Paying', payload['message'].content)
    if "Offer Has Been Accepted By" in payload['message'].content:
        payer = int(payload['message'].content.split('@')[1].split('>')[0])
        payee = int(payload['message'].content.split('@')[2].split('>')[0])
        amount = int(payload['message'].content.split(' ')[-2])

        await self.Mods.tokensRule.addTokens(self, payee,  amount)
        await self.Mods.tokensRule.addTokens(self, payer, -amount)
        self.Data['PlayerData'][payer]['Offers'] -= amount

        await payload['message'].edit(content=f"<@{payer}>'s Offer Has Been Accepted and Completed By <@{payee}> for {amount} Tokens")
        await self.Refs['channels']['actions'].send(f"<@{payer}>'s Offer Has Been Completed By <@{payee}>")

# Command
async def setOffer(self, payload):
    if payload.get('Author') not in self.moderators: return
    
    cont = payload['Content'].strip().split(' ')
    if len(cont) > 2 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id

        toset = 0
        try: toset = int(cont[2])
        except ValueError: return

        self.Data['PlayerData'][pid]['Offers'] = toset

"""
Function Called on Reaction
"""
async def on_reaction(self, payload):
    if payload['emoji'] == '✔️' and payload['Channel'] == 'market':
        await acceptOffer(self, payload)
    if payload['emoji'] == '✔️' and payload['Channel'] == 'actions' and f"{payload['user'].name}#{payload['user'].discriminator}" in self.moderators:
        await payOffer(self, payload)