import time, discord, io

zipChan = list(zip(['Suber-Votes-1','Suber-Votes-2', 'Suber-Votes-3', 'Suber-Votes-4'],  [ 'voting-1','voting-2','voting-3','voting-4',]))
maxSuberCount = 12

whipEmojiMap = "1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟".split(' ')
endorseEmojiMap = ['👍', '👎', 'ℹ️']

async def create_array(self):
    def keySort(key): return int(self.Data['Subers'][key]['Proposal#']) 
    
    def keySortSub(key):
        return float(f"-{len(self.Data['Subers'][key[0]][key[1]]['Supporters'])}{1e10 - self.Data['Subers'][key[0]][key[1]]['DOB'].timestamp()}")

    # Sorted list of player IDs In order of Proposal Parent
    sortedArrays = list(sorted( dict(self.Data['Subers']).keys(), key=keySort))
    messages = [m async for m in self.Refs['channels']['array'].history(limit=100)]
    

    # If Array Length not right size, regenerate to keep uniform spacing.
    if self.Data.get('Subers-MSG') is None or len(self.Data.get('Subers-MSG')) != maxSuberCount : 
        await self.Refs['channels']['array'].purge()
        print('   |   Purging Array', self.Data.get('Subers-MSG') , maxSuberCount )

        self.Data['Subers-MSG'] = []
        for pid in range(maxSuberCount):  
            msg = await self.Refs['channels']['array'].send(".")
            self.Data['Subers-MSG'].append( [msg.id, ".", None] )
        await create_array(self)
        return
        


    # Update Messages with Stats
    toSend = []
    for ai in range(len(sortedArrays)):
        suberKey  = sortedArrays[ai]
        arrayMajorMinors = list(sorted( [(suberKey, 'Assenter'), (suberKey, 'Dissenter')], key=keySortSub))

        indexMajorMinors = 0
        for suberKey, MajorOrMinor in arrayMajorMinors:        
            idx = -1-(ai*2 + indexMajorMinors  )     
            mid, oldLine, oldfilename = self.Data['Subers-MSG'][idx]
            indexMajorMinors += 1
           
            # Generate Message Content

            # Whip Nominate Phase
            cont = ""
            files  = []
            filename = ""
            emojis = []

            if  self.Data['Subers'][suberKey][MajorOrMinor]['Proposal'] in ['', None]:
                self.Data['Subers'][suberKey][MajorOrMinor]['Supporters'] = []

            if self.Data['Subers'][suberKey][MajorOrMinor]['Is Official']:
                filename = f"0-{suberKey}-{MajorOrMinor}-{self.Data['Subers'][suberKey][MajorOrMinor]['DOB']}.txt"
                player = self.Data['PlayerData'][self.Data['Subers'][suberKey][MajorOrMinor]['Whip']]['Name']

                if self.Data['Subers'][suberKey][MajorOrMinor]['Proposal'] is None or len(self.Data['Subers'][suberKey][MajorOrMinor]['Proposal']) <= 1: 
                    cont   = f"**Proposal {suberKey}'s {MajorOrMinor} SUBER:** Suber {self.Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip:" \
                             f"{player} Has No Proposal."
                    files  = []
                else: 
                    cont   = f"**Proposal {suberKey}'s {MajorOrMinor} SUBER:** Suber {self.Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip:" \
                             f"{player} (Supporters: {len(self.Data['Subers'][suberKey][MajorOrMinor]['Supporters'])})"
                    files  = [discord.File(fp=io.StringIO(self.Data['Subers'][suberKey][MajorOrMinor]['Proposal']), filename=filename),]
                
                emojis += endorseEmojiMap
            else:
                filename = f"0-{suberKey}-{MajorOrMinor}-{self.Data['Subers'][suberKey]['Date']}.txt"
                if len(self.Data['Subers'][suberKey][MajorOrMinor]['Whip']) == 0:
                    cont = f"**Proposal {suberKey}'s {MajorOrMinor} SUBER:** Vote for a WHIP by reacting to denote an Affirmative Vote\n" \
                           f"   WHIPs can nominate themselves by clicking 🎗️ \n\n No Whips Have Nominated Themselves." 
                    SupportRecord = "Whips Nominee Support Record:\n\n No Whips Have Nominated Themselves."

                    filename = str(abs(hash(SupportRecord)) % (10 ** 8)) + filename
                    files  = [discord.File(fp=io.StringIO(SupportRecord), filename=filename)]

                else:
                    cont  = f"**Proposal {suberKey}'s {MajorOrMinor} SUBER:** Vote for a WHIP by reacting to denote an Affirmative Vote\n" \
                            f"   WHIPs can nominate themselves by clicking 🎗️\n\nWhip Nominees:"
                    for i in range(len(self.Data['Subers'][suberKey][MajorOrMinor]['Whip'])):
                        cont += f"\n {whipEmojiMap[i]} : "
                        cont += f"{self.Data['PlayerData'][self.Data['Subers'][suberKey][MajorOrMinor]['Whip'][i]['Name']]['Name']}"
                        cont += f" ({len(self.Data['Subers'][suberKey][MajorOrMinor]['Whip'][i]['Supporters'])})"
                            
                    # Generate Support Record
                    SupportRecord = "Whips Nominee Support Record:\n\n"
                    for i in range(len(self.Data['Subers'][suberKey][MajorOrMinor]['Whip'])):
                        whip = self.Data['Subers'][suberKey][MajorOrMinor]['Whip'][i]['Name']
                        s = f"\n{self.Data['PlayerData'][whip]['Name']} Supporters:\n"
                        for sup in self.Data['Subers'][suberKey][MajorOrMinor]['Whip'][i]['Supporters']:
                            s += f"   -{self.Data['PlayerData'][sup]['Name']}\n"
                        SupportRecord += s

                    filename = str(abs(hash(SupportRecord)) % (10 ** 8)) + filename
                    files  = [self.discord.File(fp=io.StringIO(SupportRecord), filename=filename)]
                                   
                emojis.append('🎗️')
                for e in whipEmojiMap[:len(self.Data['Subers'][suberKey][MajorOrMinor]['Whip'])]: 
                    emojis.append(e)

            # Update Message Content
            if  ( oldfilename != filename) or \
                ( oldLine != cont ):
                try: msg = await self.Refs['channels']['array'].fetch_message(mid) 
                except: 
                    self.Data['Subers-MSG'] = []
                    await create_array(self)
                    return
                print('   |   Editing Array', suberKey, idx)
                await msg.edit( content = cont, attachments = files)
                self.Data['Subers-MSG'][idx] = [mid, cont, filename]
                for e in whipEmojiMap + endorseEmojiMap + ['🎗️',]:
                    hasEmoji = False
                    for r in msg.reactions: 
                        if str(r) == e: hasEmoji = True
                    if not hasEmoji and e     in emojis: await msg.add_reaction(   e            )
                    if     hasEmoji and e not in emojis: await msg.remove_reaction(e, msg.author)
    
    for ai in range(len(sortedArrays)*2, maxSuberCount):
        idx = -1-ai
        mid, oldLine, oldfilename = self.Data['Subers-MSG'][idx]
        if oldLine != ".":  
            try: msg = await self.Refs['channels']['array'].fetch_message(mid) 
            except: 
                self.Data['Subers-MSG'] = []
                await create_array(self)
                return
            print('   |   Editing Array to blank', idx)
            await msg.edit(content = ".", attachments = [])
            self.Data['Subers-MSG'][idx] = [mid, ".", None]
            if len(msg.reactions) > 0:
                for r in msg.reactions: await msg.remove_reaction(r , msg.author)

    print('   |   Array Updated')
    self.Data['Array'] = sortedArrays[::-1]
    return self.Data

# schedule
async def suberTick(self): # ( Done )
    def keySortSub(arr):
        return len(arr['Supporters'])
    
    for suberKey in list(self.Data['Subers'].keys()): 
        minority = self.Data['Subers'][suberKey]['Loser']

        # Tally Whip Votes
        if self.Data['Subers'][suberKey]['Turn'] +1 <= self.Data['Turn']:

            majority = ['Assenter', 'Dissenter']
            majority.remove(minority)
            majority = majority[0]


            # Not Loser Tally
            if not self.Data['Subers'][suberKey][majority]['Is Official']:
                # Set Whip Majority

                arrayMajorMinors = list(self.Data['Subers'][suberKey][majority]['Whip'])
                arrayMajorMinors.sort(key=keySortSub)
                print(arrayMajorMinors)
                if len(arrayMajorMinors) > 0 and self.Data['Subers'][suberKey][minority]['Is Official'] and \
                len(arrayMajorMinors[0]['Supporters']) >  len(self.Data['Subers'][suberKey][majority]["Members"])*0.5 and \
                (len(arrayMajorMinors) == 1 or len(arrayMajorMinors[0]['Supporters']) != len(arrayMajorMinors[1]['Supporters'])):
                    self.Tasks.update(set([
                        self.set_data(['Subers',suberKey,majority,'Whip'], arrayMajorMinors[0]['Name']),
                        self.set_data(['Subers',suberKey,majority,'Is Official'], True),
                    ]))
                    cont = f"Proposal {suberKey}'s SUBER: {self.Data['PlayerData'][arrayMajorMinors[0]['Name']]['Name']} has been elected as a Whip." 
                    await self.Refs['channels']['actions'].send(cont)


            # Loser Tally
            if not self.Data['Subers'][suberKey][minority]['Is Official']:
                arrayMajorMinors = list(sorted( self.Data['Subers'][suberKey][minority]['Whip'], key=keySortSub))

                # If No Whip Consensis Vote
                if len(arrayMajorMinors) == 0 or (len(arrayMajorMinors) != 1 and \
                len(arrayMajorMinors[0]['Supporters']) <=  len(self.Data['Subers'][suberKey][minority]['Members'])*0.5 and \
                len(arrayMajorMinors[0]['Supporters']) == len(arrayMajorMinors[1]['Supporters'])):
                    cont = f"Proposal {suberKey}'s SUBER: Disbanded Due To Failed Majority Vote of Minority Whip" 
                    await self.Refs['channels']['actions'].send(cont)
                    del self.Data['Subers'][suberKey]
                    continue

                # Set Whip Minority
                else:
                    self.Tasks.update(set([
                        self.set_data(['Subers',suberKey,minority,'Whip'], arrayMajorMinors[0]['Name']),
                        self.set_data(['Subers',suberKey,minority,'Is Official'], True)
                    ]))
                    cont = f"Proposal {suberKey}'s SUBER: {self.Data['PlayerData'][arrayMajorMinors[0]['Name']]['Name']} has been elected as a Whip." 
                    await self.Refs['channels']['actions'].send(cont)
                

        # Week Expiration Test
        if (self.Data['Day'] - self.Data['Subers'][suberKey]['Date']) > 7:
            cont = f"Proposal {suberKey}'s SUBER's Week Expiration Reached. Suber is Disbanded " 
            await self.Refs['channels']['actions'].send(cont)
            del self.Data['Subers'][suberKey]

    await create_array(self)
  
# schedule
async def popSuber(self): # (Done
    def keySortSub(key):
        return float(f"-{len(self.Data['Subers'][key[0]][key[1]]['Supporters'])}{1e10 - self.Data['Subers'][key[0]][key[1]]['DOB'].timestamp()}")

    # Reset Channels
    votesCopy = dict()
    for subChan, disChan in list(zipChan): 
        votesCopy[subChan] = self.Data[subChan]
        if disChan == 'voting': self.Data[subChan]['Suber'] = None
        votesCopy[subChan]['ProposingPlayer'] = None
        votesCopy[subChan]['ProposingMSGs']   = []
        votesCopy[subChan]['ProposingText']   = ""
        await self.Refs['channels'][disChan].set_permissions(self.Refs['roles']['Player'], send_messages=False)

    # Suber Channels
    usedChan = []
    for suberKey in self.Data['Subers'].keys(): 
        MajorOrMinor = list(sorted( [(suberKey, 'Assenter'), (suberKey, 'Dissenter')], key=keySortSub))[0][-1]
        print('MM',MajorOrMinor)
        pid  = self.Data['Subers'][suberKey][MajorOrMinor]['Whip']
        if len(self.Data['Subers'][suberKey][MajorOrMinor]['Proposal']) > 1:
            for subChan, disChan in list(zipChan): 
                if disChan == 'voting' or subChan in usedChan: continue
                if self.Data[subChan]['ProposingPlayer'] is None:
                    print("   |   Pop Suber", subChan, MajorOrMinor, "into", subChan, disChan )
                    votesCopy[subChan] = { 'Yay':[], 'Nay':[], 'Abstain':[], 'ProposingMSGs':[], 'ProposingPlayer':pid,
                        'Suber':f"Proposal {suberKey}'s SUBER: Suber {self.Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip:",
                        'ProposingText':                          str(self.Data['Subers'][suberKey][MajorOrMinor]['Proposal']),
                        'Proposal#':self.Data['Proposal#'], 'SuberKey':suberKey
                        }
                    self.Data['Proposal#'] =+ 1
                    self.Tasks.update(set([
                        self.set_data(['Subers',suberKey,MajorOrMinor,'File'],       ''),
                        self.set_data(['Subers',suberKey,MajorOrMinor,'Supporters'], []),
                        self.set_data(['Subers',suberKey,MajorOrMinor,'Proposal'],   ''),
                        self.set_data(['Subers',suberKey,MajorOrMinor,'DOB'],        self.now())
                    ]))
                    usedChan.append(subChan)

                    print('   |   - PopProposal To Suber: ',suberKey, MajorOrMinor)
                    await self.Refs['channels'][disChan].set_permissions(self.Refs['roles']['Player'], send_messages=True)
                    break
    for key in votesCopy.keys():
        self.Tasks.add( self.set_data([key,], votesCopy[key]) )

                

# schedule
async def suber_tally(self): #( Done )
    # Tally SUBERS
    for chan in ['Suber-Votes-1','Suber-Votes-2', 'Suber-Votes-3', 'Suber-Votes-4']: 
        if self.Data[chan]['ProposingPlayer'] is None: continue
        player        = self.Data['PlayerData'][ self.Data[chan]['ProposingPlayer'] ]['Name']
        votingPlayers  = len(self.Data[chan]['Yay']) + len(self.Data[chan]['Nay'])
        activePlayers = len(self.Refs['roles']['Player'].members) - len(self.Refs['roles']['Inactive'].members)

        if len(self.Data[chan]['ProposingText']) < 1: continue
        if len(self.Data[chan]['Yay']) > len(self.Data[chan]['Nay']):
            await self.Refs['channels']['actions'].send(f" - {player}'s SUBER Proposal Passes\n" \
                f"- Tally: {len(self.Data[chan]['Yay'])} For, {len(self.Data[chan]['Nay'])} Against.\nSUBER is Disbanded\n\n")
            del self.Data['Subers'][self.Data[chan]['SuberKey']]

        else:
            await self.Refs['channels']['actions'].send(f" - {player}'s SUBER Proposal Failed \n" \
                f"- Tally: {len(self.Data[chan]['Yay'])} For, {len(self.Data[chan]['Nay'])} Against.\n\n")
            for line in proposalText(self, chan):
                await self.Refs['channels']['failed-proposals'].send(line)

# funtion (Done)
def proposalText(self, voteChan):
    playerprop = self.Data[voteChan]['ProposingPlayer']
    if playerprop is None: return []

    msg = f"Proposal #{self.Data[voteChan]['Proposal#']}: "
    if voteChan != 'Votes': msg += self.Data[voteChan]['Suber']
    if not self.Data['VotingEnabled']: msg += f"**Status: ({len(self.Data[voteChan]['Yay'])} For, {len(self.Data[voteChan]['Nay'])} Against.)** \n\n "
    else                             : msg += "**Status: Voting Closed** \n\n "
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
async def actuallyUpdateVotingProposal(self):
    def is_proposalMSG(m): 
        for chan in channelMap.keys():
            if m.id in self.Data[chan]['ProposingMSGs']: return True
        return False

    last_update_prop_time = time.time()
    hold_for_update_prop = False
    

    for subChan, disChan in zipChan:
        lines = proposalText(self, subChan)

        if len(lines) != len(self.Data[subChan]['ProposingMSGs']):
            self.Data[subChan]['ProposingMSGs'] = []
            for line in lines:
                msg = await self.Refs['channels'][disChan].send(line)
                self.Data[subChan]['ProposingMSGs'].append([msg.id, line])
        for i in range(len(self.Data[subChan]['ProposingMSGs'])): 
            mid, old_line = self.Data[subChan]['ProposingMSGs'][i] 
            line = lines[i]
            if line != old_line:
                try: msg = await self.Refs['channels'][disChan].fetch_message(mid) 
                except: 
                    self.Data[subChan]['ProposingMSGs'] = []
                    await actuallyUpdateVotingProposal(self)
                    return
                await msg.edit(content = line)
                self.Data[subChan]['ProposingMSGs'][i] = [mid, line]

"""
Main Run Function On Messages (Done)
"""
async def on_message(self, payload):
    isInactive = self.Refs['players'][payload['raw'].author.id].get_role(self.Refs['roles']['Inactive'].id) is not None

    if payload['Channel'] in self.Mods.votingRule.channelMap.keys() and payload['Channel'] != "voting":
        # Remove MSG if from a non Player (Bot, Illegal, Etc)
        if payload['Author ID'] not in self.Data['PlayerData'] or self.Data['VotingEnabled']:
            print('   |   Suber Removing', payload['Content'])
            await payload['raw'].delete()
            return
        
        # Enable Activity
        await self.Mods.inactivityRule.activeOnVote(self, payload['Author ID'])

        # Register Vote
        vote = payload['Content'].lower().strip()
        if vote in self.Mods.votingRule.yayVotes:
            await self.Mods.votingRule.yay(self, payload)
            await payload['raw'].add_reaction('✔️')
        elif vote in self.Mods.votingRule.nayVotes:
            await self.Mods.votingRule.nay(self, payload)
            await payload['raw'].add_reaction('✔️')
        elif vote in self.Mods.votingRule.abstainVotes:
            await self.Mods.votingRule.abstain(self, payload)
            await payload['raw'].add_reaction('✔️')
        else:
            await payload['raw'].add_reaction('❌')
            await self.dm(payload['raw'].author.id, "Your vote is ambigious, Please use appropriate yay, nay, or withdraw text." )
            return

    if payload['Channel'] == 'suber-proposals': # Done For Nomic 4
        isWhipFor = []
        pid = payload['Author ID']
        for suberKey in self.Data['Subers'].keys():
            for MajorOrMinor in ['Assenter', 'Dissenter']:
                if self.Data['Subers'][suberKey][MajorOrMinor]['Is Official'] and payload['Author ID'] == self.Data['Subers'][suberKey][MajorOrMinor]['Whip']:
                    isWhipFor.append([suberKey, MajorOrMinor])

        if   len(isWhipFor) == 0:
            try: await payload['raw'].author.send( content = "You are not a WHIP for any SUBERs")
            except Exception as e: print(f"Error sending msg to { payload['raw'].author.id }, {e}")
        
        elif len(isWhipFor) == 1:
            suberKey     = isWhipFor[0][0]
            MajorOrMinor = isWhipFor[0][1]

            if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
                decoded = await list(payload['Attachments'].values())[0].read()
                decoded = decoded.decode(encoding="utf-8", errors="strict")
                self.Data['Subers'][suberKey][MajorOrMinor]['Proposal'] = str(decoded)

            if len(payload['Attachments']) == 0:
                self.Data['Subers'][suberKey][MajorOrMinor]['Proposal'] = str(payload['Content'])

            print("   |   Prop:", self.Data['Subers'][suberKey][MajorOrMinor]['Proposal'])
            self.Data['Subers'][suberKey][MajorOrMinor]['DOB']        = self.now()
            self.Data['Subers'][suberKey][MajorOrMinor]['Supporters'] = [pid, ]
            await create_array(self)
             
        elif len(isWhipFor) > 1:
            cont = "Please indicate which SUBER you are Proposing to:"
            options = {}
            for i in range(len(isWhipFor)):                
                suberKey     = isWhipFor[i][0]
                MajorOrMinor = isWhipFor[i][1]
                cont += f"\n   {whipEmojiMap[i]} : Proposal {suberKey}'s SUBER"
                options[whipEmojiMap[i]] = isWhipFor[i]

            msg = None
            try: msg = await payload['raw'].author.send( content = cont)
            except Exception as e: 
                print(f"Error sending msg to { payload['raw'].author.id }, {e}")
                return
            if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
                decoded = await list(payload['Attachments'].values())[0].read()
                proposalText = decoded.decode(encoding="utf-8", errors="strict")
            if len(payload['Attachments']) == 0:
                proposalText = payload['Content']
            
            for e in whipEmojiMap[:len(isWhipFor)]: 
                await msg.add_reaction(e)

            self.Data['PlayerData'][pid]['Query'] = {
                "Type": 'ArrayProposal',
                "Options": options,
                "ProposalText": proposalText,
                "msgid": msg.id
            }
    await actuallyUpdateVotingProposal(self)


async def on_reaction(self, payload): # (Done)
    isInactive = payload['user'].get_role(self.Refs['roles']['Inactive'].id) is not None

    if payload['Channel'] == 'array' and payload['mode'] == 'add':

        await payload['message'].remove_reaction(payload['emoji'] , payload['user'])

        # If not "Is Official"
        if len(payload['Attachments']) == 0: return

        suberKey     = int(list(payload['Attachments'].keys())[0].split("-")[1])
        MajorOrMinor =     list(payload['Attachments'].keys())[0].split("-")[2]
        
        if suberKey not in self.Data['Subers']:
            print("Failed Suber Emoji", self.Data['Subers'].keys(), suberKey)
            return

        # Nominate Yourself
        if payload['emoji'] == '🎗️':
            if not self.Data['Subers'][suberKey][MajorOrMinor]['Is Official']:
                for i in self.Data['Subers'][suberKey][MajorOrMinor]['Whip']: 
                    if i['Name'] == payload['user'].id: return
                if payload['user'].id not in self.Data['Subers'][suberKey][MajorOrMinor]['Members']: 
                    await payload['user'].send( content = "You are not a member of this Suber Side")
                    return
                if not self.Data['Subers'][suberKey][self.Data['Subers'][suberKey]['Loser']]['Is Official'] and self.Data['Subers'][suberKey]['Loser'] != MajorOrMinor:
                    await payload['user'].send( content = "You must wait for the Minority Whip To be Elected before nominating Majority Whips")
                    return
                self.Data['Subers'][suberKey][MajorOrMinor]['Whip'].append({'Name':payload['user'].id, 'Supporters':[payload['user'].id], 'DOB':self.now()})
                await actuallyUpdateVotingProposal(self)
                await create_array(self)
        
        # Choose a Whip
        if payload['emoji'] in whipEmojiMap:
            if not self.Data['Subers'][suberKey][MajorOrMinor]['Is Official']:
                endorsedIndex = whipEmojiMap.index(payload['emoji'])
                if payload['user'].id not in self.Data['Subers'][suberKey][MajorOrMinor]['Members']: 
                    await payload['user'].send( content = "You are not a member of this Suber Side")
                # Remove On Re-Click
                elif payload['user'].id in self.Data['Subers'][suberKey][MajorOrMinor]['Whip'][endorsedIndex]['Supporters']: 
                    self.Data['Subers'][suberKey][MajorOrMinor]['Whip'][endorsedIndex]['Supporters'].remove(payload['user'].id)    
                # Append On Click
                elif endorsedIndex < len(self.Data['Subers'][suberKey][MajorOrMinor]['Whip']):
                    for whipKey in range(len(self.Data['Subers'][suberKey][MajorOrMinor]['Whip'])):
                        if payload['user'].id in self.Data['Subers'][suberKey][MajorOrMinor]['Whip'][whipKey]['Supporters']:
                            self.Data['Subers'][suberKey][MajorOrMinor]['Whip'][whipKey]['Supporters'].remove(payload['user'].id)                    
                    self.Data['Subers'][suberKey][MajorOrMinor]['Whip'][endorsedIndex]['Supporters'].append(payload['user'].id)
                else: return         
                await actuallyUpdateVotingProposal(self)
                await create_array(self)

        # Endorse Proposal
        if self.Data['Subers'][suberKey][MajorOrMinor]['Is Official'] and payload['emoji'] == '👍':
            if payload['user'].id not in self.Data['Subers'][suberKey][MajorOrMinor]['Supporters']:
                self.Data['Subers'][suberKey][MajorOrMinor]['Supporters'].append(payload['user'].id)
                await actuallyUpdateVotingProposal(self)
                await create_array(self)

        # Unendorse Proposal
        if self.Data['Subers'][suberKey][MajorOrMinor]['Is Official'] and payload['emoji'] == '👎':
            if payload['user'].id in self.Data['Subers'][suberKey][MajorOrMinor]['Supporters']:
                self.Data['Subers'][suberKey][MajorOrMinor]['Supporters'].remove(payload['user'].id)
                await actuallyUpdateVotingProposal(self)
                await create_array(self)

        # Get Info
        if self.Data['Subers'][suberKey][MajorOrMinor]['Is Official'] and payload['emoji'] == 'ℹ️':
            msg = f"**\nProposal {suberKey}'s SUBER: Suber {self.Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip Supporters:**\n"
            for p in self.Data['Subers'][suberKey][MajorOrMinor]['Supporters']: msg += '\n - ' + self.Data['PlayerData'][p]['Name']
            await self.dm(payload['user'],msg)
            msg = f"**\nProposal {suberKey}'s SUBER: Suber {self.Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip Proposal:**\n"
            await self.send(payload['user'],msg)

    # If Query Answer
    if payload['Channel'] == 'DM' and payload['mode'] == 'add' and \
    self.Data['PlayerData'][payload['user'].id]['Query'] is not None and \
    self.Data['PlayerData'][payload['user'].id]['Query']["msgid"] == payload['message'].id:
        if self.Data['PlayerData'][payload['user'].id]['Query']["Type"] == 'ArrayProposal':
            suberKey     = self.Data['PlayerData'][payload['user'].id]['Query']["Options"][payload['emoji']][0]
            MajorOrMinor = self.Data['PlayerData'][payload['user'].id]['Query']["Options"][payload['emoji']][1]
            
            self.Data['Subers'][suberKey][MajorOrMinor]['Proposal']   = str(self.Data['PlayerData'][payload['user'].id]['Query']["ProposalText"])
            self.Data['Subers'][suberKey][MajorOrMinor]['DOB']        = self.now()
            self.Data['Subers'][suberKey][MajorOrMinor]['Supporters'] = [payload['user'].id, ]
            
            self.Data['PlayerData'][payload['user'].id]['Query'] = None 

            await payload['message'].add_reaction('✔️')
            await actuallyUpdateVotingProposal(self)
            await create_array(self)

async def update(self):
    await create_array(self)
    await actuallyUpdateVotingProposal(self)