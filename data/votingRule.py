
#
# Voting System Module For Discord Bot
################################
import pickle, sys, time, io, discord, datetime, urllib, re, random
channelMap = {
        'voting': 'Votes',
        'voting-1': 'Suber-Votes-1',
        'voting-2': 'Suber-Votes-2',
        'voting-3': 'Suber-Votes-3',
        'voting-4': 'Suber-Votes-4',
}

last_update_prop_time = 0
hold_for_update_prop = False

last_update_deck_time = 0
hold_for_update_deck = False


yayEmojis = []
yayVotes  = [ "aye", "yay", "yes", "y", "ye", "pog", "ya", "noice", "cash money", "yeah", "heck yeah", "hell yeah"]            

nayEmojis = []
nayVotes  = ["nay", "no", "n", "nah", "nein", "sus", "cringe", "soggy"]

abstainEmojis = []
abstainVotes  = ['abstain', 'withdraw']


# schedule (Done)
async def bot_tally(self):
    # Tally Main Voting Queue
    if self.Data['Votes']['ProposingPlayer'] is None or len(self.Data['Votes']['ProposingText']) <= 1:
            await self.Refs['channels']['actions'].send(f"**Vote Status:** No Proposal was on Deck")
    else:
        player = "Undefined"
        isDoom = 0
        if self.Data['Votes']['ProposingPlayer'] == "DOOM":
            player = "Intentional Game Design"
            isDoom = 1
        else:
            player = self.Data['PlayerData'][ self.Data['Votes']['ProposingPlayer'] ]['Name']

        votingPlayers = len(self.Data['Votes']['Yay']) + len(self.Data['Votes']['Nay'])
        activePlayers = len(self.Refs['roles']['Player'].members) - len(self.Refs['roles']['Inactive'].members)
        losers        = None


        # Tally Main Voting ( Nomitron 4 Safe)
        if len(self.Data['Votes']['ProposingText']) <= 1:
            await self.Refs['channels']['actions'].send(f"**Vote Status:** No Proposal was on Deck\n\n" )

        elif len(self.Data['Votes']['Yay']) + isDoom > len(self.Data['Votes']['Nay']):
            losers = ['Dissenter','Nay']
            await self.Refs['channels']['actions'].send(f"**Vote Status:**  {player}'s Proposal Passes\n" \
                f"- Tally: {len(self.Data['Votes']['Yay'])} For, {len(self.Data['Votes']['Nay'])} Against.")
        else:
            losers = ['Assenter','Yay']
            await self.Refs['channels']['actions'].send(f"**Vote Status:**  {player}'s Proposal Failed \n" \
                f"- Tally: {len(self.Data['Votes']['Yay'])} For, {len(self.Data['Votes']['Nay'])} Against.")
            for line in proposalText(self, 'Votes'):
                await self.Refs['channels']['failed-proposals'].send(line)
         
         
        # Form SUBERS if necassary
        print('   |   - SUBER', len(self.Data['Votes'][losers[1]]) , votingPlayers, activePlayers)
        if votingPlayers == 0: return
        if len(self.Data['Votes'][losers[1]])  >= 0.2 * votingPlayers and (activePlayers <= 2 * votingPlayers):
            self.Tasks.add(
                self.set_data(['Subers',self.Data['Votes']['Proposal#']], {
                    'Proposal#' : self.Data['Votes']['Proposal#'],
                    'Assenter': {
                        'Members':self.Data['Votes']['Yay'], 'Is Official': False, 'Whip' : [],
                        'Proposal' : "", 'Supporters' : [],'DOB' : self.now(),
                        'Party': ['Minority', 'Majority'][losers == "Yay"]
                    },
                    'Dissenter': {
                        'Members':self.Data['Votes']['Nay'], 'Is Official': False, 'Whip' : [],
                        'Proposal' : "", 'Supporters' : [], 'DOB' : self.now(),
                        'Party': ['Minority', 'Majority'][losers == "Nay"]
                    },
                    'Date': self.Data['Day']+1, 'Turn': self.Data['Turn']+1, 'Voting Channel': None, 'Loser' : losers[0]
                }
            ))
           
            await self.Refs['channels']['actions'].send(
                f"**A SUBER has been formed! \n" \
                f"   Assenters:  {' '.join([f'<@{pid}>' for pid in self.Data['Votes']['Yay'] ])}\n\n" \
                f"   Dissenters: {' '.join([f'<@{pid}>' for pid in self.Data['Votes']['Nay'] ])}\n\n"
            )

# funtion (Done)
def proposalText(self, voteChan):
    playerprop = self.Data[voteChan]['ProposingPlayer']
    if playerprop is None: return []

    msg = f"Proposal #{self.Data[voteChan]['Proposal#']}: "
    if voteChan != 'Votes': msg += self.Data[voteChan]['Suber']
    if self.Data['VotingEnabled'] or voteChan != 'Votes': msg += f"**Status: ({len(self.Data[voteChan]['Yay'])} For, {len(self.Data[voteChan]['Nay'])} Against.)** \n\n "
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
    
    last_update_prop_time = time.time()
    hold_for_update_prop = False

    lines = proposalText(self, 'Votes')
   
    if not self.Data['VotingEnabled'] or len(self.Data['Votes']['ProposingMSGs']) == 0 \
        or len(self.Data['Votes']['ProposingMSGs']) != len(lines):
        if len(lines) != len(self.Data['Votes']['ProposingMSGs']):
            print('   |   Resending Voting Proposal')
            for msg in self.Data['Votes']['ProposingMSGs']: await msg.delete()
            self.Data['Votes']['ProposingMSGs'] = []
            for line in lines:
                msg = await self.Refs['channels']['voting'].send(line)
                self.Data['Votes']['ProposingMSGs'].append([msg.id, line])

    for i in range(len(self.Data['Votes']['ProposingMSGs'])): 
        if isinstance(self.Data['Votes']['ProposingMSGs'][i], int):
            self.Data['Votes']['ProposingMSGs'][i] = [self.Data['Votes']['ProposingMSGs'][i], lines[i]]
        mid, line  = self.Data['Votes']['ProposingMSGs'][i] 
        if line != lines[i]:   
            print('   |   Editing Voting Proposal')
            try: msg = await self.Refs['channels']['voting'].fetch_message(mid) 
            except: 
                self.Data['Votes']['ProposingMSGs'] = []
                await updateProposal(self)
                return
            await msg.edit(content = lines[i])
            self.Data['Votes']['ProposingMSGs'][i] = [mid, lines[i]]

# shedule, Command, Function
async def enableVoting(self, payload = None):
    if payload is not None and payload.get('Author') not in self.moderators: return
    print('   |   Enabling Voting')
    self.Data['VotingEnabled'] = True

    for disChan in channelMap.keys(): 
        await self.Refs['channels'][disChan].set_permissions(self.Refs['roles']['Player'], send_messages=False)
    await self.Refs['channels']['voting'].set_permissions(self.Refs['roles']['Player'], send_messages=True)
    await self.Refs['channels']['actions'].send("-  Players May Now Vote in #voting.")
    for p in self.Refs['players'].values(): await p.remove_roles(self.Refs['roles']['On Deck'])
    await updateProposal(self)

# schedule (Done)
async def popProposal(self, payload = None):
    if payload is not None and payload.get('Author') not in self.moderators: return
    def keySortSub(key):
        return float(f"-{len(self.Data['Subers'][key[0]][key[1]]['Supporters'])}{1e10 - self.Data['Subers'][key[0]][key[1]]['DOB'].timestamp()}")

    # Reset Channels
    votesCopy = dict(self.Data['Votes'])
    votesCopy['ProposingPlayer'] = None
    votesCopy['ProposingMSGs']   = []
    votesCopy['ProposingText']   = ""
    self.Tasks.add( self.Refs['channels']['voting'].set_permissions(self.Refs['roles']['Player'], send_messages=False) )

    # Voting Channel
    print('   |   PopProposal To Deck:')
    gotProp = False
    if len(self.Data['Queue']) > 0: 
        pid = self.Data['Queue'][0]
        if len(self.Data['PlayerData'][pid]['Proposal']['File']) > 1: 
            self.Tasks.add( self.set_data(['Queue'],  self.Data['Queue'][1:] ) )
            print('   |   - Popping Proposal: ', self.Data['PlayerData'][pid]['Name'])

            if len(self.Data['PlayerData'][pid]['Proposal']['File']) > 1: 
                for k,p in self.Refs['players'].items():  
                    if k != pid: self.Tasks.add( p.remove_roles(self.Refs['roles']['On Deck']) )
                    else:        self.Tasks.add( p.add_roles(   self.Refs['roles']['On Deck']) )
                
                votesCopy = { 'Yay':[], 'Nay':[], 'Abstain':[], 'ProposingMSGs':[], 'ProposingPlayer':pid,
                                'ProposingText':str(self.Data['PlayerData'][pid]['Proposal']['File']),
                                'Proposal#':self.Data['Proposal#']}
                self.Data['Proposal#'] += 1
                self.Tasks.update(set([
                    self.set_data(['PlayerData',pid,'Proposal','File'],       ''),
                    self.set_data(['PlayerData',pid,'Proposal','Supporters'], []),
                    self.set_data(['PlayerData',pid,'Proposal','DOB'], self.now())
                ]))
                gotProp = True
                self.schedule(
                    name = 'Enable Voting', 
                    function = enableVoting, 
                    parameter = 'Day',
                    nextTime = self.Data['Day'] + 1,
                    interval = None
                )
                self.updateSchedule('End Of Turn', delta = self.day)

    # Doom Proposal
    if not gotProp:
        print('   |   - No Proposal In Queue')
        votesCopy = { 'Yay':[], 'Nay':[], 'Abstain':[], 'ProposingMSGs':[], 'ProposingPlayer':"DOOM",
                            'ProposingText':str("A Doom Proposal Shall Be Determined By Mods"),
                            'Proposal#':self.Data['Proposal#']}
        self.Data['Proposal#'] += 1 
        self.schedule(
            name = 'Enable Voting', 
            function = enableVoting, 
            parameter = 'Day',
            nextTime = self.Data['Day'] + 1,
            interval = None
        )
        self.updateSchedule('End Of Turn', delta = self.day)
    else:
        await self.Refs['channels']['game'].send("<@250132828950364174> does the wording of this proposal have your certified Daniel seal of approval?")

    self.Tasks.add( self.set_data(['Votes'], votesCopy ) )
    self.Tasks.add( self.set_data(['VotingEnabled'], False ) )

    await updateProposal(self)
    await create_queue(self)

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
        await create_queue(self.Data, payload)

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

        # Attempt to become active
        await self.Mods.inactivityRule.activateOnEndorse(self, payload['user'].id)

        # Update is things Changed
        if updateQueue: await create_queue(self)
 

"""
Main Run Function On Messages (Done)
"""
async def on_message(self, payload):
    isInactive = self.Refs['players'][payload['raw'].author.id].get_role(self.Refs['roles']['Inactive'].id) is not None

    if payload['Channel'] in ['voting',]:

        # Remove MSG if from a non Player (Bot, Illegal, Etc)
        if payload['Author ID'] not in self.Data['PlayerData'] or not self.Data['VotingEnabled']:
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
            await self.Mods.suitsRule.rewardMethod(self,payload['Author ID'], 'Vote')
        elif vote in nayVotes:
            await nay(self, payload)
            await payload['raw'].add_reaction('✔️')
            await self.Mods.suitsRule.rewardMethod(self,payload['Author ID'], 'Vote')
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
        if self.Data['VotingEnabled'] == True: 
            await self.Refs['channels']['deck-edits'].send("The deck cannot be updated at this time in the turn.")
            return
        if payload['Author ID'] != self.Data['Votes']['ProposingPlayer']: 
            await self.Refs['channels']['deck-edits'].send("You are not the proposer. This message will be ignored.")
            return

        if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
            decoded = await list(payload['Attachments'].values())[0].read()
            decoded = decoded.decode(encoding="utf-8", errors="strict")
            self.Data['Votes']['ProposingText'] = decoded

        if len(payload['Attachments']) == 0:
            self.Data['Votes']['ProposingText'] = payload['Content']
        await updateProposal(self)
 
    if payload['Channel'] == 'emergency-deck-edits':
        print('   |   Updating E. Deck Proposal')
        if self.Data['VotingEnabled'] == False: 
            await self.Refs['channels']['deck-edits'].send("The emergency-deck cannot be updated at this time in the turn.")
            return
        if payload['Author ID'] != self.Data['Votes']['ProposingPlayer']: 
            await self.Refs['channels']['deck-edits'].send("You are not the proposer. This message will be ignored.")
            return

        if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
            decoded = await list(payload['Attachments'].values())[0].read()
            decoded = decoded.decode(encoding="utf-8", errors="strict")
            self.Data['Votes']['ProposingText'] = decoded

        if len(payload['Attachments']) == 0:
            self.Data['Votes']['ProposingText'] = payload['Content']
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
