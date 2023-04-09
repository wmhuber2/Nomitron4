
#
# Voting System Module For Discord Bot
################################
import pickle, sys, time, io, discord, datetime, urllib, re, random
from copy import *
channelMap = {
        'voting'  : 'Votes',
        'voting-1': 'Votes-1',
        'voting-2': 'Votes-2',
        'voting-3': 'Votes-3',
        'voting-4': 'Votes-4',
        'voting-5': 'Votes-5',
}
defaultDict = {
                'Yay':[], 'Nay':[], 
                'Abstain':[], 'Proposal': {}, 
                'ProposingMSGs':{},
                'ProposingPlayer':None, 
                'ProposingText':"", 
                'Proposal#': 0,
                'Suber': None,
                'Haymaker': None,
                'VotingEnabled': False
            }


yayEmojis = []
yayVotes  = [ "aye", "yay", "yes", "y", "ye", "pog", "ya", "noice", "cash money", "yeah", "heck yeah", "hell yeah"]            

nayEmojis = []
nayVotes  = ["nay", "no", "n", "nah", "nein", "sus", "cringe", "soggy"]

abstainEmojis = []
abstainVotes  = ['abstain', 'withdraw']

suberEmojis = ['♻️',]

# schedule (Done)
async def bot_tally(self):
    # Tally Main Voting Queue
    for chanName, chanKey in channelMap.items():
        if self.Data[chanKey]['ProposingPlayer'] is None or len(self.Data[chanKey]['ProposingText']) <= 1:
            continue

        player = "Undefined"
        isDoom = self.Data[chanKey]['ProposingPlayer'] == "DOOM"
        isSuber = self.Data[chanKey].get('Suber') is not None
        isHaymaker = self.Data[chanKey].get('Haymaker') is not None

        if not isDoom: player = self.Data['PlayerData'][ self.Data[chanKey]['ProposingPlayer'] ]['Name']

       
        votingPlayers = len(self.Data[chanKey]['Yay']) + len(self.Data[chanKey]['Nay'])
        activePlayers = len(self.Refs['roles']['Player'].members) - len(self.Refs['roles']['Inactive'].members)
        subersPlayers = -1
        losers        = None

        chan = self.Refs['channels'].get(chanName)
        mid, line = self.Data[chanKey]['ProposingMSGs'][-1]
        try:  
            msg = await chan.fetch_message(mid)
            for emoji in msg.reactions:
                if str(emoji.emoji) in suberEmojis:
                    subersPlayers += emoji.count 
        except Exception as e:  print('Error: Lost Voting MSG in Bot-Count', e)



        # Tally Main Voting ( Nomitron 4 Safe)
        if len(self.Data[chanKey]['Yay']) + 0.5*int(isDoom) > len(self.Data[chanKey]['Nay']):
            losers = ['Dissenter','Nay']
            await self.Refs['channels']['actions'].send(f"- **Vote Status:**  {player}'s {'SUBER ' if isSuber else ''}Proposal Passes\n" \
                f"  Tally: {len(self.Data[chanKey]['Yay'])} For, {len(self.Data[chanKey]['Nay'])} Against.")
        else:
            losers = ['Assenter','Yay']
            await self.Refs['channels']['actions'].send(f"- **Vote Status:**  {player}'s {'SUBER ' if isSuber else ''}Proposal Failed \n" \
                f"  Tally: {len(self.Data[chanKey]['Yay'])} For, {len(self.Data[chanKey]['Nay'])} Against.")
            for line in proposalText(self, chanKey):
                await self.Refs['channels']['failed-proposals'].send(line)
        


        # Form SUBERS if necassary
        if not isSuber and not isHaymaker:
            print('   |   - SUBER', len(self.Data[chanKey][losers[1]]) , votingPlayers, activePlayers, subersPlayers)
            if votingPlayers == 0: return
            if (activePlayers <= 2 * votingPlayers) and (subersPlayers >= 0.2 * votingPlayers):
                #if len(self.Data[chanKey][losers[1]])  >= 0.2 * votingPlayers and (activePlayers <= 2 * votingPlayers):
                self.Tasks.add(
                    self.set_data(['Subers',self.Data[chanKey]['Proposal#']], {
                        'Proposal#' : int(self.Data[chanKey]['Proposal#']),
                        'Assenter': {
                            'Members':self.Data[chanKey]['Yay'], 'Is Official': False, 'Whip' : [],
                            'Proposal' : "", 'Supporters' : [],'DOB' : self.now(),
                            'Party': ['Minority', 'Majority'][losers == "Yay"]
                        },
                        'Dissenter': {
                            'Members':self.Data[chanKey]['Nay'], 'Is Official': False, 'Whip' : [],
                            'Proposal' : "", 'Supporters' : [], 'DOB' : self.now(),
                            'Party': ['Minority', 'Majority'][losers == "Nay"]
                        },
                        'Date': self.Data['Day']+1, 'Turn': self.Data['Turn']+1, 'Voting Channel': None, 'Loser' : losers[0]
                    }
                ))
            
                await self.Refs['channels']['actions'].send(
                    f"**A SUBER has been formed! **\n" \
                    f"   Assenters:  {' '.join([f'<@{pid}>' for pid in self.Data[chanKey]['Yay'] ])}\n\n" \
                    f"   Dissenters: {' '.join([f'<@{pid}>' for pid in self.Data[chanKey]['Nay'] ])}\n\n"
                )

# funtion (Done)
def proposalText(self, voteChan):
    playerprop = self.Data[voteChan]['ProposingPlayer']
    if playerprop is None: return []

    msg = f"Proposal #{self.Data[voteChan]['Proposal#']}: "
    if self.Data[voteChan]['VotingEnabled']: msg += f"**Status: ({len(self.Data[voteChan]['Yay'])} For, {len(self.Data[voteChan]['Nay'])} Against.)** \n\n "
    else                    : msg += "**Status: ON DECK (No Voting)** \n\n "
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

# function (Done)
async def updateProposal(self):
    for chanName, chanKey in channelMap.items():
        # Get, Update And Create Voting Channels
        chan = self.Refs['channels'].get(chanName)
        if chan is None:
            overwrites = {
                self.Refs['roles'][self.moderatorRole]: self.discord.PermissionOverwrite(read_messages=True,  send_messages=True),
                self.Refs['roles']['Bot']:              self.discord.PermissionOverwrite(read_messages=True,  send_messages=True),
                self.server.default_role:               self.discord.PermissionOverwrite(read_messages=True, send_messages=False),
            }
            chan = await self.server.create_text_channel(chanName, overwrites=overwrites, category= self.Refs['category']['business'])
            self.Refs['channels'][chan.name] = chan
            self.Data[chanKey] = deepcopy(defaultDict)
            print('   |   Added Voting Channel:', chan.name, chanName)
        
        if chanKey not in self.Data: self.Data[chanKey] = deepcopy(defaultDict) 
        for k in defaultDict.keys():
            if k not in self.Data[chanKey]:
                self.Data[chanKey][k] = deepcopy(defaultDict[k])

        # Update Text
        if   self.Data[chanKey].get(   'Suber') is not None:
            lines = self.Mods.suberRule.proposalText(self, chanKey)
        elif self.Data[chanKey].get('Haymaker') is not None:
            lines = self.Mods.haymakerRule.proposalText(self, chanKey)
        else:
            lines = proposalText(self, chanKey)
    
        # Update Channel
        needToEdit = len(self.Data[chanKey]['ProposingMSGs']) != len(lines)
        for i in range(len(self.Data[chanKey]['ProposingMSGs'])):
            if needToEdit: break
            if lines[i] != self.Data[chanKey]['ProposingMSGs'][i][1]:
                needToEdit=True
        
        if not needToEdit: continue
        if not self.Data[chanKey]['VotingEnabled'] \
            or len(self.Data[chanKey]['ProposingMSGs']) != len(lines):
            print('   |   Resending Voting Proposal',chanKey)
            for mid, line in self.Data[chanKey]['ProposingMSGs']: 
                try:
                    msg = await chan.fetch_message(mid) 
                    await msg.delete()
                except: 
                    print('Error: Lost Voting MSG')
            self.Data[chanKey]['ProposingMSGs'] = []
            for line in lines:
                msg = await chan.send(line)
                self.Data[chanKey]['ProposingMSGs'].append([msg.id, line])
            
            if  self.Data[chanKey].get(   'Suber') is None \
                and self.Data[chanKey].get('Haymaker') is None:
                for e in suberEmojis: await msg.add_reaction(e)

        for i in range(len(self.Data[chanKey]['ProposingMSGs'])): 
            if isinstance(self.Data[chanKey]['ProposingMSGs'][i], int):
                self.Data[chanKey]['ProposingMSGs'][i] = [self.Data[chanKey]['ProposingMSGs'][i], lines[i]]
            mid, line  = self.Data[chanKey]['ProposingMSGs'][i] 
            if i >= len(lines):
                await msg.edit(content = '.')
                self.Data[chanKey]['ProposingMSGs'][i] = [mid, '.']
            elif line != lines[i]:   
                print('   |   Editing Voting Proposal',chanKey)
                try: msg = await chan.fetch_message(mid) 
                except: 
                    self.Data[chanKey]['ProposingMSGs'] = []
                    await updateProposal(self)
                    return
                await msg.edit(content = lines[i])
                self.Data[chanKey]['ProposingMSGs'][i] = [mid, lines[i]]

# shedule, Command, Function
async def enableVoting(self, payload = None, channelKey = None):
    if payload is not None and payload.get('Author') not in self.moderators: return
    if payload is not None: channelKey = payload['Channel']

    for chan in channelMap.keys():
        if chan != channelKey and channelKey is not None: continue
        if self.Data[channelMap[chan]]['ProposingPlayer'] is None: continue

        print('   |   Enabling Voting', chan)
        self.Data[channelMap[chan]]['VotingEnabled'] = True

        await self.Refs['channels'][chan].set_permissions(self.Refs['roles']['Player'], send_messages=True)
        await self.Refs['channels']['actions'].send(f"-  Players May Now Vote in #{chan}.")
        print(self.Data[channelMap[chan]]['ProposingPlayer'])
        if self.Data[channelMap[chan]]['ProposingPlayer'] in self.Refs['players'].keys():
            self.Tasks.add( 
                self.Refs['players'][self.Data[channelMap[chan]]['ProposingPlayer']].remove_roles( 
                    self.Refs['roles']['On Deck']
                ) 
            )                
    if channelKey is None:    
        await updateProposal(self)

# shedule, Command, Function
async def disableVoting(self, payload = None, channelKey = None):
    if payload is not None and payload.get('Author') not in self.moderators: return
    if payload is not None: channelKey = payload['Channel']

    for chan in channelMap.keys():
        if chan != channelKey and channelKey is not None: continue
        if self.Data[channelMap[chan]]['ProposingPlayer'] is None: continue

        print('   |   Disabling Voting', chan)
        self.Data[channelMap[chan]]['VotingEnabled'] = False

        await self.Refs['channels'][chan].set_permissions(self.Refs['roles']['Player'], send_messages=False)
        #await self.Refs['channels']['actions'].send(f"-  Vote in #{chan}.")
    if channelKey is None:    
        await updateProposal(self)

# schedule (Done)
async def popProposal(self, payload = None):
    if payload is not None and payload.get('Author') not in self.moderators: return
    def keySortSub(key):
        return float(f"-{len(self.Data['Subers'][key[0]][key[1]]['Supporters'])}{1e10 - self.Data['Subers'][key[0]][key[1]]['DOB'].timestamp()}")

    # Determine How Many Props to Pop From Queue
    nQueue = 0
    for pid in self.Data['Queue']: 
        if self.Data['PlayerData'][pid]['Proposal']['File'] is not None and len(self.Data['PlayerData'][pid]['Proposal']['File']) > 1: 
           nQueue += 1

    nQueue = int(nQueue/6) +1
    sliceQueue    = self.Data['Queue'][:nQueue]
    sliceHaymaker = self.Data['Haymaker'][:1]
    sliceArray    = list(self.Data['Subers'].keys())
    self.Tasks.add( self.set_data(['Queue'], self.Data['Queue'][nQueue:] ) )
    print('   |   PopProposal To Deck:', len(sliceQueue))


    # Pop Proposals
    gotProp = False
    for k,p in self.Refs['players'].items(): await p.remove_roles(self.Refs['roles']['On Deck']) 
    for chanName, chanKey in channelMap.items():
        # Reset Channels
        votesCopy = deepcopy(defaultDict)
        
        # QUEUE
        if len(sliceQueue) > 0: 
            pid = sliceQueue.pop(0)
            if len(self.Data['PlayerData'][pid]['Proposal']['File']) > 1: 
                print('   |   - Popping Proposal: ', self.Data['PlayerData'][pid]['Name'])

                self.Tasks.add( self.Refs['players'][pid].add_roles( self.Refs['roles']['On Deck']) )
                
                votesCopy.update({ 'ProposingPlayer':pid,
                                   'ProposingText':str(self.Data['PlayerData'][pid]['Proposal']['File']),
                                   'Proposal#': int(self.Data['Proposal#'])})
                self.Data['Proposal#'] += 1
                self.Tasks.update(set([
                    self.set_data(['PlayerData',pid,'Proposal','File'],       ''),
                    self.set_data(['PlayerData',pid,'Proposal','Supporters'], []),
                    self.set_data(['PlayerData',pid,'Proposal','DOB'], self.now())
                ]))
                self.Tasks.add( self.set_data([chanKey], votesCopy ) )
                gotProp = True
                self.Tasks.add( disableVoting(self, channelKey = chanName) )
                await self.Refs['channels']['game'].send("<@250132828950364174> does the wording of this proposal have your certified Daniel seal of approval?")

        # SUBERS
        elif len(sliceQueue) == 0 and len(sliceArray) > 0:
            while 1:
                if len(sliceArray) == 0: break
                suberKey = sliceArray.pop(0)
                MajorOrMinor = list(sorted( [(suberKey, 'Assenter'), (suberKey, 'Dissenter')], key=keySortSub))[0][-1]
                print('MM',MajorOrMinor)
                pid  = self.Data['Subers'][suberKey][MajorOrMinor]['Whip']
                if len(self.Data['Subers'][suberKey][MajorOrMinor]['Proposal']) > 1:
                    print("   |   Pop Suber", pid, suberKey, MajorOrMinor, "into", chanKey )
                    votesCopy.update({  'ProposingPlayer':pid,
                                        'Suber':f"Proposal {suberKey}'s SUBER: Suber {self.Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip:",
                                        'ProposingText':                          str(self.Data['Subers'][suberKey][MajorOrMinor]['Proposal']),
                                        'Proposal#':int(self.Data['Proposal#']), 
                                        'SuberKey':suberKey,
                                        'VotingEnabled': True
                                    })
                    self.Data['Proposal#'] =+ 1
                    self.Tasks.update(set([
                        self.set_data(['Subers',suberKey,MajorOrMinor,'File'],       ''),
                        self.set_data(['Subers',suberKey,MajorOrMinor,'Supporters'], []),
                        self.set_data(['Subers',suberKey,MajorOrMinor,'Proposal'],   ''),
                        self.set_data(['Subers',suberKey,MajorOrMinor,'DOB'],        self.now())
                    ]))
                    self.Tasks.add( self.set_data([chanKey], votesCopy ) )
                    print('   |   - PopProposal To Suber: ',suberKey, MajorOrMinor)
                    self.Tasks.add( enableVoting(self, channelKey = chanName) )
                    break
                        
        # Haymakers
        elif len(sliceQueue) == 0 and len(sliceArray) == 0 and len(sliceHaymaker) > 0:
            pid, name = sliceHaymaker.pop(0)
            print(pid, name)
            nActivePlayers = len(self.Refs['roles']['Player'].members) - len(self.Refs['roles']['Inactive'].members)
            if len(self.Data['PlayerData'][pid]["DI's"][ name ]['File']) > 1 \
               and len(self.Data['PlayerData'][pid]["DI's"][ name ]['Supporters']) > 0.3 * nActivePlayers: 
                print('   |   - Popping Proposal: ', self.Data['PlayerData'][pid]['Name'])

                self.Tasks.add( self.Refs['players'][pid].add_roles( self.Refs['roles']['On Deck']) )
                
                votesCopy.update({ 'ProposingPlayer':pid,
                                   'ProposingText':str(self.Data['PlayerData'][pid]["DI's"][ name ]['File']),
                                   'Proposal#':int(self.Data['Proposal#']),
                                   'Haymaker':name})
                self.Data['Proposal#'] += 1
                self.Tasks.add( self.Mods.haymakerRule.removeDI(self,pid, name) )
                self.Tasks.add( self.set_data([chanKey], votesCopy ) )
                self.Tasks.add( enableVoting(self, channelKey = chanName) )
                gotProp = True
                #await self.Refs['channels']['game'].send("<@250132828950364174> does the wording of this proposal have your certified Daniel seal of approval?")
        else:
            self.Tasks.add( disableVoting(self, channelKey = chanName) )

                
    # Doom Proposal
    if gotProp:
        self.schedule(
            name = 'Enable Voting', 
            function = enableVoting, 
            parameter = 'Day',
            nextTime = self.Data['Day'] + 1,
            interval = None
        )
        self.updateSchedule('End Of Turn', delta = self.day)
    else:
        print('   |   - No Proposal In Queue')
        votesCopy.update({ 'ProposingPlayer':"DOOM",
                           'ProposingText':str("A Doom Proposal Shall Be Determined By Mods"),
                           'Proposal#':int(self.Data['Proposal#'])})
        self.Data['Proposal#'] += 1 
        self.schedule(
            name = 'Enable Voting', 
            function = enableVoting, 
            parameter = 'Day',
            nextTime = self.Data['Day'] + 1,
            interval = None
        )
        self.updateSchedule('End Of Turn', delta = self.day)
        await self.Refs['channels']['game'].send("<@250132828950364174> does the wording of this proposal have your certified Daniel seal of approval?")

    #self.Tasks.add( updateProposal(self) )
    #self.Tasks.add( create_queue(self) )

# command (Done)
async def yay(self, payload):
    author = payload['Author ID']
    if self.clientid == author: author = payload['user'].id
    voteKey = channelMap[payload['Channel']]
    if author not in self.Data[voteKey]['Yay']:           self.Data[voteKey]['Yay'].append( author )
    if author in self.Data[voteKey]['Nay']:               self.Data[voteKey]['Nay'].remove( author )
    if author in self.Data[voteKey]['Abstain']:           self.Data[voteKey]['Abstain'].remove( author )
    #await payload['message'].remove_reaction(nayEmoji , payload['user'])

# command (Done)
async def nay(self, payload):
    author = payload['Author ID']
    if self.clientid == author: author = payload['user'].id
    voteKey = channelMap[payload['Channel']]
    if author not in self.Data[voteKey]['Nay']:           self.Data[voteKey]['Nay'].append( author )
    if author in self.Data[voteKey]['Yay']:               self.Data[voteKey]['Yay'].remove( author )
    if author in self.Data[voteKey]['Abstain']:           self.Data[voteKey]['Abstain'].remove( author )
    #await payload['message'].remove_reaction(yayEmoji , payload['user'])

# command (Done)
async def abstain(self, payload):
    author = payload['Author ID']
    if self.clientid == author: author = payload['user'].id
    voteKey = channelMap[payload['Channel']]
    if author not in self.Data[voteKey]['Abstain']:       self.Data[voteKey]['Abstain'].append( author )
    if author in self.Data[voteKey]['Yay']:               self.Data[voteKey]['Yay'].remove( author )
    if author in self.Data[voteKey]['Nay']:               self.Data[voteKey]['Nay'].remove( author )
    #await payload['message'].remove_reaction(nayEmoji , payload['user'])

# command (Done)
async def removeProposal(self, payload):
    if payload.get('Author') not in self.moderators: return 

    playerid = payload['Content'].split(' ')[1]
    player = await self.getPlayer(playerid, payload)
    pid = player.id
    print('   |   Purging proposals for ',player.name)

    self.Data['PlayerData'][pid]['Proposal'] = {}
    self.Data['PlayerData'][pid]['Proposal']['File'] = ''
    self.Data['PlayerData'][pid]['Proposal']['Supporters'] = []
    self.Data['PlayerData'][pid]['Proposal']['DOB'] = self.now()

    await create_queue(self)

# command (Done)
async def setProposalNumber(self, payload):
    if payload.get('Author') not in self.moderators: return
    try: self.Data['Proposal#'] = int(payload['Content'].split(' ')[1])
    except Exception as e: print(e)
    await payload['raw'].channel.send(f"Set Proposal Number to {self.Data['Proposal#']}")
 
"""
Function Called on Reaction (Done)
"""
async def on_reaction(self, payload):
    if payload['Channel'] == 'voting' and payload['mode'] == 'add': # Fixed
        if   payload['emoji'] in yayEmojis:          await yay(self, payload)
        elif payload['emoji'] in nayEmojis:          await nay(self, payload)
        elif payload['emoji'] in abstainEmojis:      await abstain(self, payload)
        else: return
    
        self.Mods.inactivityRule.forceActivate(self, payload['user'].id)

    if payload['Channel'] == 'queue' and payload['mode'] == 'add':
        await payload['message'].remove_reaction(payload['emoji'] , payload['user'])

        # Ignore is no proposal on queue entry
        if len(payload['Attachments']) == 0: return

        # Proposal Owener From Encoded ID in File Name
        author   = int(list(payload['Attachments'].keys())[0].split("-")[0])
        updateQueue = False

        if payload['emoji'] == '👍':
            if payload['user'].id not in self.Data['PlayerData'][author]['Proposal']['Supporters']:
                self.Data['PlayerData'][author]['Proposal']['Supporters'].append(payload['user'].id)
            updateQueue = True
            # Attempt to become active
            await self.Mods.inactivityRule.activateOnEndorse(self, payload['user'].id)
        elif payload['emoji'] == '👎':
            if payload['user'].id in self.Data['PlayerData'][author]['Proposal']['Supporters']:
                self.Data['PlayerData'][author]['Proposal']['Supporters'].remove(payload['user'].id)
            updateQueue = True
        elif payload['emoji'] == 'ℹ️':
            # List Create MSG Header
            msg = f"------\n **{self.Data['PlayerData'][author]['Name']}'s Proposal Info:**\n"

            # Create Supporters
            msg +=  f"```Supporters:"
            for p in self.Data['PlayerData'][author]['Proposal']['Supporters']: msg += '\n - ' + self.Data['PlayerData'][p]['Name']
            msg += "```"
            await self.send(payload['user'],msg)
            
            # Create Proposal Text
            msg = "**Proposal:**\n"
            msg += self.Data['PlayerData'][author]['Proposal']['File']

            # Send Message
            await self.send(payload['user'],msg)
        else: return


        # Update is things Changed
        if updateQueue: await create_queue(self)
 

"""
Main Run Function On Messages (Done)
"""
async def on_message(self, payload):
    isInactive = self.Refs['players'][payload['raw'].author.id].get_role(self.Refs['roles']['Inactive'].id) is not None

    if payload['Channel'] in channelMap.keys():
        chanKey = payload['Channel']

        # Remove MSG if from a non Player (Bot, Illegal, Etc)
        if payload['Author ID'] not in self.Data['PlayerData'] or not self.Data[channelMap[payload['Channel']]]['VotingEnabled']:
            print('   |   Voting Removing', payload['Content'])
            await payload['raw'].delete()
            return
        
        await self.Mods.inactivityRule.activeOnVote(self, payload['Author ID'])
        isInactive = self.Refs['players'][payload['raw'].author.id].get_role(self.Refs['roles']['Inactive'].id) is not None
        if isInactive:
            await payload['raw'].add_reaction('❌')
            return


        # Register Vote
        vote = payload['Content'].lower().strip()
        if vote in yayVotes:
            await yay(self, payload)
            await payload['raw'].add_reaction('✔️')
            await self.Mods.suitsRule.rewardMethod(self,payload['Author ID'], chanKey)
        elif vote in nayVotes:
            await nay(self, payload)
            await payload['raw'].add_reaction('✔️')
            await self.Mods.suitsRule.rewardMethod(self,payload['Author ID'], chanKey)
        elif vote in abstainVotes:
            await abstain(self, payload)
            await payload['raw'].add_reaction('✔️')
        else:
            await payload['raw'].add_reaction('❌')
            await self.dm(payload['raw'].author.id, "Your vote is ambigious, Please use appropriate yay, nay, or withdraw text." )
 
        await updateProposal(self)

    if payload['Channel'] == 'proposals':
        print('   |   Saving Proposal', payload['Content'])
        pid = payload['Author ID']

        if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
            decoded = await list(payload['Attachments'].values())[0].read()
            decoded = decoded.decode(encoding="utf-8", errors="strict")
            self.Data['PlayerData'][pid]['Proposal']['File'] = decoded

        if len(payload['Attachments']) == 0:
            self.Data['PlayerData'][pid]['Proposal']['File'] = payload['Content']

        print("   |   Prop:", self.Data['PlayerData'][pid]['Proposal']['File'])
        self.Data['PlayerData'][pid]['Proposal']['DOB'] = self.now()
        self.Data['PlayerData'][pid]['Proposal']['Supporters'] = [pid, ]
        await self.Mods.inactivityRule.activateOnEndorse(self, pid)
        await create_queue(self)

    if payload['Channel'] == 'deck-edits':
        print('   |   Updating Deck Proposal')
        votingChans = []
        for chanName, chanKey in channelMap.items():
            if payload['Author ID'] == self.Data[chanKey]['ProposingPlayer'] \
            and not self.Data[chanKey]['VotingEnabled']: 
                votingChans.append(chanKey)

        if len(votingChans) == 0:
            await self.Refs['channels']['deck-edits'].send("There are no decks can be edited by you at this time in the turn.")
            return
        if len(votingChans) == 1:
            votingChan = votingChans[0]

            if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
                decoded = await list(payload['Attachments'].values())[0].read()
                decoded = decoded.decode(encoding="utf-8", errors="strict")
                self.Data[votingChan]['ProposingText'] = decoded
            if len(payload['Attachments']) == 0:
                self.Data[votingChan]['ProposingText'] = payload['Content']
        await updateProposal(self)
 
    if payload['Channel'] == 'emergency-deck-edits':
        print('   |   Updating E. Deck Proposal')
        votingChans = []
        for chanName, chanKey in channelMap.items():
            if payload['Author ID'] == self.Data[chanKey]['ProposingPlayer'] \
            and self.Data[chanKey]['VotingEnabled']: 
                votingChans.append(chanKey)

        if len(votingChans) == 0:
            await self.Refs['channels']['emergency-deck-edits'].send("There are no decks that can be edited by you at this time in the turn.")
            return
        if len(votingChans) == 1:
            votingChan = votingChans[0]

            if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
                decoded = await list(payload['Attachments'].values())[0].read()
                decoded = decoded.decode(encoding="utf-8", errors="strict")
                self.Data[votingChan]['ProposingText'] = decoded
            if len(payload['Attachments']) == 0:
                self.Data[votingChan]['ProposingText'] = payload['Content']
        await updateProposal(self)


"""
Update Function Called Every 10 Seconds (Done)
"""
async def update(self):
    await create_queue(self)
    await updateProposal(self)


"""
Update the QUEUE
"""
async def create_queue(self):
    def keySort(key):
        stri = (int(len(self.Data['PlayerData'][key]['Proposal']['Supporters']) + int(len(self.Data['PlayerData'][key]['Proposal']['File']) > 1)) << 32 ) | ((1 << 32) - int(self.Data['PlayerData'][key]['Proposal']['DOB'].timestamp()))
        return stri


    # Sorted list of player IDs In order of Suporters, then Age
    sortedQ = list(sorted( dict(self.Data['PlayerData']).keys(), key=keySort))
    self.Data['Queue'] = sortedQ[::-1]


    # If Queue Structure not right size, regenerate to keep uniform spacing.
    if self.Data.get('Queue-MSGS') is None or len(self.Data['Queue-MSGS']) != len(sortedQ): 
        await self.Refs['channels']['queue'].purge()
        self.Data['Queue-MSGS'] = []
        for pid in sortedQ:  
            msg = await self.Refs['channels']['queue'].send("Generating Proposal View")
            self.Data['Queue-MSGS'].append([msg.id, "Generating Proposal View", None])
            for r in ['👍', '👎', 'ℹ️']: await msg.add_reaction(r)
    
    willBeEndorsing = set()

    # Update Messages with Stats
    for i in list(range(len(sortedQ))):
        mid, oldLine, oldfilename = self.Data['Queue-MSGS'][i]
        pid     = sortedQ[i]
        player  = self.Data['PlayerData'][pid]['Name']

        filename = f"{pid}-{self.Data['PlayerData'][pid]['Proposal']['DOB']}.txt"

        # Generate Message Content
        if self.Data['PlayerData'][pid]['Proposal']['File'] is None or len(self.Data['PlayerData'][pid]['Proposal']['File']) <= 1: 
            cont   = f"{player} Has No Proposal."
            files  = []
        else: 
            cont   = f"{player}'s Proposal: (Supporters: {len(self.Data['PlayerData'][pid]['Proposal']['Supporters'])})"
            files  = [discord.File(fp=io.StringIO(self.Data['PlayerData'][pid]['Proposal']['File']), filename=filename),]
            if  pid != self.Data['Queue'][0]: willBeEndorsing.update(self.Data['PlayerData'][pid]['Proposal']['Supporters'])
        

        # Update Message Content
        if oldfilename != filename or cont != oldLine:
            try: msg = await self.Refs['channels']['queue'].fetch_message(mid) 
            except: 
                self.Data['Queue-MSGS'] = []
                await create_queue(self)
                return
            print('   |   Editing Queue', player)
            await msg.edit( content = cont, attachments = files)
            self.Data['Queue-MSGS'][i] = [mid, cont, filename]
        
            # Add MSG Badge
            if len(self.Data['PlayerData'][pid]['Proposal']['File']) <= 1:  
                if ('🥇' in list(map(str,msg.reactions))):  await msg.clear_reaction('🥇') #1st
                if ('🥈' in list(map(str,msg.reactions))):  await msg.clear_reaction('🥈') #1st
                if ('🥉' in list(map(str,msg.reactions))):  await msg.clear_reaction('🥉') #1st
                continue

            if len(self.Data['Queue']) <= 0: pass
            elif  (not '🥇' in list(map(str,msg.reactions))) and pid == self.Data['Queue'][0]:   await msg.add_reaction('🥇')
            elif      ('🥇' in list(map(str,msg.reactions))) and pid != self.Data['Queue'][0]:   await msg.clear_reaction('🥇') #1st
            
            if len(self.Data['Queue']) <= 1: pass
            elif  (not '🥈' in list(map(str,msg.reactions))) and pid == self.Data['Queue'][1]:   await msg.add_reaction('🥈')
            elif      ('🥈' in list(map(str,msg.reactions))) and pid != self.Data['Queue'][1]:   await msg.clear_reaction('🥈') #2st
            
            if len(self.Data['Queue']) <= 2: pass
            elif  (not '🥉' in list(map(str,msg.reactions))) and pid == self.Data['Queue'][2]:   await msg.add_reaction('🥉')
            elif      ('🥉' in list(map(str,msg.reactions))) and pid != self.Data['Queue'][2]:   await msg.clear_reaction('🥉') #3st
        

    #print('   |   Queue Updated')
