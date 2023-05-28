
#
# Voting System Module For Discord Bot
################################
import pickle, sys, time, io, discord, datetime, urllib, re, random
import base64

emojiMap = "1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟".split(' ')
async def giveDI(self, payload):  
    pid = payload['Author ID']
    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |   Giving DI to ', player.name)
        if self.Data['PlayerData'][pid].get("DI's") is None:
            self.Data['PlayerData'][pid]["DI's"] = {}

        counter = 1
        for k,v in self.Data['PlayerData'][pid]["DI's"].items():
            if f"On Turn {self.Data['Turn']}" in k:
                counter +=1
        name = f"Judement #{counter} On Turn {self.Data['Turn']}"
        self.Data['PlayerData'][pid]["DI's"][ name ] = {
            'Expiration Date': self.Data['Time'] + self.week,
            'File': "",
            'Supporters':[],
            'DOB':self.now()
        }
        
        self.schedule(
            name = f"Expiration of DI for \"Judement #{counter} On Turn {self.Data['Turn']}\"", 
            function = removeDI, 
            parameter = 'Time',
            nextTime = self.now() + self.week,
            interval = self.week,
            varis    = {'pid':pid, 'name':name}
        )

        await payload['raw'].add_reaction('✔️')

async def removeDI(self, pid, name):
    try: del self.Data['PlayerData'][pid]["DI's"][name]
    except: pass

# funtion (Done)
def proposalText(self, voteChan):
    playerprop = self.Data[voteChan]['ProposingPlayer']
    if playerprop is None: return []

    msg = f"Proposal #{self.Data[voteChan]['Proposal#']}: "
    if voteChan != 'Votes': msg += self.Data[voteChan]['Haymaker']
    if not self.Data['VotingEnabled']: msg += f"** Status: ({len(self.Data[voteChan]['Yay'])} For, {len(self.Data[voteChan]['Nay'])} Against.)** \n\n "
    else                             : msg += "** Status: Voting Closed** \n\n "
    topin = []

    for line in self.Data[voteChan]['ProposingText'].split('\n'):
        line += '\n'
        if len(msg + line) > 1920:
            topin.append(msg)
            msg = ""

            for word in line.split(' '):
                if len(msg + word) > 1920:
                    topin.append(msg)
                    msg = str(word)
                else: msg += word
                msg += " "
        else: msg += line
    if len(msg) > 1: topin.append(msg)
    return topin

"""
Function Called on Reaction (Done)
"""
async def on_reaction(self, payload):
     # If Query Answer
    if payload['Channel'] == 'DM' and payload['mode'] == 'add' and \
    self.Data['PlayerData'][payload['user'].id]['Query'] is not None and \
    self.Data['PlayerData'][payload['user'].id]['Query']["msgid"] == payload['message'].id:
        if self.Data['PlayerData'][payload['user'].id]['Query']["Type"] == 'HaymakerProposal':
            name     = self.Data['PlayerData'][payload['user'].id]['Query']["Options"][payload['emoji']]
            pid      = payload['user'].id
            self.Data['PlayerData'][pid]["DI's"][ name ]['File']   = str(self.Data['PlayerData'][pid]['Query']["ProposalText"])
            self.Data['PlayerData'][pid]["DI's"][ name ]['DOB']        = self.now()
            self.Data['PlayerData'][pid]["DI's"][ name ]['Supporters'] = [pid, ]
            
            self.Data['PlayerData'][pid]['Query'] = None 

            await payload['message'].add_reaction('✔️')
            await create_haymaker(self)

    if payload['Channel'] == 'haymaker' and payload['mode'] == 'add':
        await payload['message'].remove_reaction(payload['emoji'] , payload['user'])

        # Ignore is no proposal on queue entry
        if len(payload['Attachments']) == 0: return

        # Proposal Owener From Encoded ID in File Name
        pid   = int(list(payload['Attachments'].keys())[0].split("--")[0])
        name = str(list(payload['Attachments'].keys())[0].split("--")[1]).replace('hashhash','#').replace('_',' ')

        updateQueue = False

        if payload['emoji'] == '🐴':
            if payload['user'].id not in self.Data['PlayerData'][pid]["DI's"][ name ]['Supporters']:
                self.Data['PlayerData'][pid]["DI's"][ name ]['Supporters'].append(payload['user'].id)
            updateQueue = True
        elif payload['emoji'] == '👎':
            if payload['user'].id in self.Data['PlayerData'][pid]["DI's"][ name ]['Supporters']:
                self.Data['PlayerData'][pid]["DI's"][ name ]['Supporters'].remove(payload['user'].id)
            updateQueue = True
        elif payload['emoji'] == 'ℹ️':
            # List Create MSG Header
            msg = f"------\n **{self.Data['PlayerData'][pid]['Name']}'s Proposal Info:**\n"

            # Create Supporters
            msg +=  f"```Supporters:"
            for p in self.Data['PlayerData'][pid]["DI's"][ name ]['Supporters']: msg += '\n - ' + self.Data['PlayerData'][p]['Name']
            msg += "```"
            await self.send(payload['user'],msg)
            
            # Create Proposal Text
            msg = "**Proposal:**\n"
            msg += self.Data['PlayerData'][pid]["DI's"][ name ]['File']

            # Send Message
            await self.send(payload['user'],msg)
        else: return

        # Update is things Changed
        if updateQueue: await create_haymaker(self)
 

"""
Main Run Function On Messages (Done)
"""
async def on_message(self, payload):
    isInactive = self.Refs['players'][payload['raw'].author.id].get_role(self.Refs['roles']['Inactive'].id) is not None
    isJudge    = self.Refs['players'][payload['raw'].author.id].get_role(self.Refs['roles']['Judge'].id) is not None

    if payload['Channel'] == 'haymaker-proposals':
        pid = payload['Author ID']
        hasDIfor = list(self.Data['PlayerData'][pid]["DI's"].keys())
        
        if   len(hasDIfor) == 0:
            await self.dm(pid, "You have no DI's")
            
        elif len(hasDIfor) == 1:
            name     = hasDIfor[0]

            if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
                decoded = await list(payload['Attachments'].values())[0].read()
                decoded = decoded.decode(encoding="utf-8", errors="strict")
                self.Data['PlayerData'][pid]["DI's"][ name ]['File'] = str(decoded)

            if len(payload['Attachments']) == 0:
                self.Data['PlayerData'][pid]["DI's"][ name ]['File'] = str(payload['Content'])

            print("   |   Prop:", self.Data['PlayerData'][pid]["DI's"][ name ]['File'])
            self.Data['PlayerData'][pid]["DI's"][ name ]['DOB']        = self.now()
            self.Data['PlayerData'][pid]["DI's"][ name ]['Supporters'] = [pid, ]
            await create_haymaker(self)
             
        elif len(hasDIfor) > 1:
            cont = "Please indicate which DI you are submitting for:"
            options = {}
            for i in range(len(hasDIfor)):                
                cont += f"\n   {emojiMap[i]} : DI {hasDIfor[i]} Proposla"
                options[emojiMap[i]] = hasDIfor[i]

            msg = await self.dm(payload['Author ID'], cont)
           
            if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
                decoded = await list(payload['Attachments'].values())[0].read()
                proposalText = decoded.decode(encoding="utf-8", errors="strict")
            if len(payload['Attachments']) == 0:
                proposalText = payload['Content']
            
            for e in emojiMap[:len(hasDIfor)]: 
                await msg.add_reaction(e)

            self.Data['PlayerData'][pid]['Query'] = {
                "Type": 'HaymakerProposal',
                "Options": options,
                "ProposalText": proposalText,
                "msgid": msg.id
            }



"""
Update Function Called Every 10 Seconds (Done)
"""
async def update(self):
    await create_haymaker(self)


"""
Update the QUEUE
"""
async def create_haymaker(self):
    def keySort(key):
        stri  = float(str(
                    len(self.Data['PlayerData'][key[0]]["DI's"][ key[1] ]['Supporters']) \
                  + int(len(self.Data['PlayerData'][key[0]]["DI's"][ key[1] ]['File']) > 1)) + '.'\
                  + str(int(self.Data['PlayerData'][key[0]]["DI's"][ key[1] ]['DOB'].timestamp()))
                )
        return stri

    channelName = 'haymaker'
    if self.Refs['channels'].get(channelName) is None:         
        overwrites = {
            self.Refs['roles'][self.moderatorRole]: self.discord.PermissionOverwrite(read_messages=True),
            self.Refs['roles']['Bot']: self.discord.PermissionOverwrite(read_messages=True),
            self.Refs['roles']['Player']: self.discord.PermissionOverwrite(read_messages=True, send_messages=False)
        }
        channel = await self.server.create_text_channel(channelName, overwrites=overwrites, category= self.Refs['category']['business'])
        self.Refs['channels'][channelName] = channel
        print('   |   Added Channel:', channel.name)
    channelName = 'haymaker-proposals'
    if self.Refs['channels'].get(channelName) is None:         
        overwrites = {
            self.Refs['roles'][self.moderatorRole]: self.discord.PermissionOverwrite(read_messages=True),
            self.Refs['roles']['Bot']: self.discord.PermissionOverwrite(read_messages=True),
            self.Refs['roles']['Player']: self.discord.PermissionOverwrite(read_messages=True, send_messages=False)
        }
        channel = await self.server.create_text_channel(channelName, overwrites=overwrites, category= self.Refs['category']['business'])
        self.Refs['channels'][channelName] = channel
        print('   |   Added Channel:', channel.name)
    

    # Sorted list of player IDs In order of Suporters, then Age
    sortedQ = []
    for pid in self.Data['PlayerData'].keys():
        sortedQ += [ [pid,k ] for k in self.Data['PlayerData'][pid]["DI's"].keys() ]
    sortedQ = list(sorted( sortedQ, key=keySort))[::-1]
    self.Data['Haymaker'] = sortedQ


    # If Queue Structure not right size, regenerate to keep uniform spacing.
    lenOfHaymaker = 25
    if self.Data.get('Haymaker-MSGS') is None or len(self.Data['Haymaker-MSGS']) != lenOfHaymaker: 
        await self.Refs['channels']['haymaker'].purge()
        self.Data['Haymaker-MSGS'] = []
        for i in range(lenOfHaymaker):  
            msg = await self.Refs['channels']['haymaker'].send(".")
            self.Data['Haymaker-MSGS'].append([msg.id, ".", None])
            for r in ['🐴', '👎', 'ℹ️']: await msg.add_reaction(r)
        self.Data['Haymaker-MSGS'] = self.Data['Haymaker-MSGS'][::-1]
    
    # Update Messages with Stats
    for i in range(min([lenOfHaymaker, len(sortedQ)])):
        mid, oldLine, oldfilename = self.Data['Haymaker-MSGS'][i]
        pid, name = sortedQ[i]
        player    = self.Data['PlayerData'][pid]['Name']

        namesafe = name.replace('#','hashhash').replace(' ','_')
        filename = f"""{pid}--{namesafe}--{self.Data['PlayerData'][pid]["DI's"][ name ]['DOB']}.txt"""

        # Generate Message Content
        if self.Data['PlayerData'][pid]["DI's"][ name ]['File'] is None or len(self.Data['PlayerData'][pid]["DI's"][ name ]['File']) <= 1: 
            cont   = name+' Has No Proposal'
            files  = []
        else: 
            cont   = f"""{player}'s Proposal: (Supporters: {len(self.Data['PlayerData'][pid]["DI's"][ name ]['Supporters'])})"""
            files  = [discord.File(fp=io.StringIO(self.Data['PlayerData'][pid]["DI's"][ name ]['File']), filename=filename),]
            

        # Update Message Content
        if oldfilename != filename or cont != oldLine:
            try: msg = await self.Refs['channels']['haymaker'].fetch_message(mid) 
            except: 
                self.Data['Haymaker-MSGS'] = []
                await create_haymaker(self)
                return
            print('   |   Editing Haymaker', player)
            await msg.edit( content = cont, attachments = files)
            self.Data['Haymaker-MSGS'][i] = [mid, cont, filename]

    for i in range(min([lenOfHaymaker, len(sortedQ)]),lenOfHaymaker):
        mid, oldLine, oldfilename = self.Data['Haymaker-MSGS'][i]

        cont   = '.'
        files  = []
        filename = None

        if oldfilename != filename or cont != oldLine:
            try: msg = await self.Refs['channels']['haymaker'].fetch_message(mid) 
            except: 
                self.Data['Haymaker-MSGS'] = []
                await create_haymaker(self)
                return
            print('   |   Editing Haymaker')
            await msg.edit( content = cont, attachments = files)
            self.Data['Haymaker-MSGS'][i] = [mid, cont, filename]


    #print('   |   Queue Updated')
