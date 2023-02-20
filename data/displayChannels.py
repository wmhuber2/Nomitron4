import datetime, yaml

async def update(self,):
    await updateSchedules(self,)
    await updateData(self,)
    for pid in self.Data['PlayerData'].keys():
        await updatePlayer(self, pid)

async def updateSchedules(self,):
    channelName = 'schedule-info'
    maxToDisplay = 25
    ignoreScheduleList = ['Start Of Turn', 'Start Of Day']
    paramMap = {
        'Time': "(HH:MM:SS)"
    }
    msgs = {}
    toSend = []
    for sched in self.Data['Schedules']:
        if sched in ignoreScheduleList: continue
        try:
            diff = self.Data['Schedules'][sched]['nextTime'] - self.getFromDict(self.Data['Schedules'][sched]['parameter'])
            if diff < diff * 0: diff = diff * 0
            if isinstance(diff, datetime.timedelta):
                diff = str(diff + self.minute - datetime.timedelta(seconds=diff.seconds % 60)).replace(':00 ',' ')
            if self.Data['Schedules'][sched]['parameter'] in paramMap:
                msgs[sched]  = f"**{sched}** will occur in {diff} {paramMap[self.Data['Schedules'][sched]['parameter']]} \n"
            else:
                msgs[sched]  = f"**{sched}** will occur in {diff} {self.Data['Schedules'][sched]['parameter']} \n"
            
        except Exception as e:
            nt = self.Data['Schedules'][sched]['nextTime']
            ct = self.getFromDict(self.Data['Schedules'][sched]['parameter'])
            if isinstance(nt, datetime.datetime): nt = nt - datetime.timedelta(seconds=nt.second)
            if isinstance(ct, datetime.datetime): ct = ct - datetime.timedelta(seconds=ct.second)
            msgs[sched]  = f"**{sched}** is waiting for **{self.Data['Schedules'][sched]['parameter']}** \n"
            msgs[sched] += f"   To become: {nt} \n"
            msgs[sched] += f"   It is now: {ct} "
        
        msgs[sched] = msgs[sched].replace('-05:51','')

    for k in sorted(msgs.keys()): toSend.append(msgs[k].strip())

    # Create Channel
    channel = self.Refs['channels'].get(channelName)
    if channel is None:
        overwrites = {
            self.Refs['roles'][self.playerRole]: self.discord.PermissionOverwrite(read_messages=True),
            self.server.default_role: self.discord.PermissionOverwrite(read_messages=False),
        }
        channel = await self.server.create_text_channel("schedule-info", overwrites=overwrites, category= self.Refs['category']['Game-Data'])
        self.Refs['channels'][channelName] = channel
        print('      Added Channel:', channelName)

    msgs = self.Data.get('Schedule-Channel-MSGS')
    if msgs is None: msgs = []
    if len(msgs) != maxToDisplay:
        print('   |   Purging Schedule-Channel-MSGS', len(msgs) , len(toSend))
        self.Data['Schedule-Channel-MSGS'] = []
        await channel.purge()
        for i in range(maxToDisplay):
            msg = await channel.send(".")
            self.Data['Schedule-Channel-MSGS'].append([msg.id, ""])
    
    msgs = self.Data.get('Schedule-Channel-MSGS')
    for i in range(1,len(toSend)+1):
        mid, old_txt = msgs[-i]
        if old_txt != toSend[i-1]:
            try: msg = await channel.fetch_message(mid) 
            except: 
                self.Data['Schedule-Channel-MSGS'] = []
                await updateSchedules(self)
                return
            await msg.edit(content = toSend[i-1])
            self.Data['Schedule-Channel-MSGS'][-i] = [mid, toSend[i-1]]

    for i in range(len(toSend)+1, maxToDisplay+1):
        mid, old_txt = msgs[-i]
        if old_txt != ".":
            try: msg = await channel.fetch_message(mid) 
            except: 
                self.Data['Schedule-Channel-MSGS'] = []
                await updateSchedules(self)
                return
            #print('   |   Editing Schedule List')
            await msg.edit(content = ".")
            self.Data['Schedule-Channel-MSGS'][-i] = [mid, "."]

async def updatePlayer(self,pid):
    channel = None
    channelName = self.Data['PlayerData'][pid].get('Info-Channel')
    if channelName is None or self.Refs['channels'].get(channelName) is None: 
        channelName = f"{self.Data['PlayerData'][pid]['Name'].lower()}-game-data".replace('#','-').replace(' ','-')
        self.Data['PlayerData'][pid]['Info-Channel'] = channelName

        if self.Refs['channels'].get(channelName) is None:
            overwrites = {
                self.Refs['roles'][self.moderatorRole]: self.discord.PermissionOverwrite(read_messages=True),
                self.server.default_role: self.discord.PermissionOverwrite(read_messages=False),
                self.Refs['players'][pid]: self.discord.PermissionOverwrite(read_messages=True),
            }
            channel = await self.server.create_text_channel(channelName, overwrites=overwrites, category= self.Refs['category']['Game-Data'])
            self.Refs['channels'][channelName] = channel
            print('   |   Added Channel:', channel.name)
    channel = self.Refs['channels'].get(channelName)
      

    maxToDisplay = 25
    ignoreKeys = ['Proposal', 'Info-Channel', 'InactiveWarned', 'query']
    paramMap = {
        'Time': "(HH:MM:SS)",
        'EmojiHold' : 'Emoji Hold',
        'EmpathyCounter': 'Correct Mood Guesses',
        'Inactive':'Reason For Inactivity',
        'MoodGuess': 'Mood Guess',
        'Offers': "Amount of Tokens Offered In Market",
        'Challanged' : 'Has Challenged This Week'


    }
    msgs = {}
    toSend = []
    for k in self.Data['PlayerData'][pid].keys():
        if k in ignoreKeys: continue
        val = self.Data['PlayerData'][pid][k]

        if isinstance(val, dict):  val = '```'+yaml.dump(self.Data['PlayerData'][pid][k])+'```'
        if isinstance(val, datetime.datetime): val = val - datetime.timedelta(seconds=val.second)

        name = str(k)
        if name in paramMap: name = paramMap[name]
        msgs[k]  = f"**{name}**:   {val}"

        msgs[k] = msgs[k].replace('-05:51','')

    for k in sorted(msgs.keys()): toSend.append(msgs[k].strip())

    msgs = self.Data.get(f'{channelName}-MSGS')
    if msgs is None: msgs = []
    if len(msgs) != maxToDisplay:
        print(f'   |   Purging {channelName}-MSGS',  len(msgs))
        self.Data[f'{channelName}-MSGS'] = []
        await channel.purge()
        for i in range(maxToDisplay):
            msg = await channel.send(".")
            self.Data[f'{channelName}-MSGS'].append([msg.id, ""])
    
    msgs = self.Data.get(f'{channelName}-MSGS')
    for i in range(1,len(toSend)+1):
        mid, old_txt = msgs[-i]
        if old_txt != toSend[i-1]:
            try: msg = await channel.fetch_message(mid) 
            except: 
                self.Data[f'{channelName}-MSGS'] = []
                await updatePlayer(self, pid)
                return
            #print(f'   |   Editing {channelName}')
            await msg.edit(content = toSend[i-1])
            self.Data[f'{channelName}-MSGS'][-i] = [mid, toSend[i-1]]

    for i in range(len(toSend)+1, maxToDisplay+1):
        mid, old_txt = msgs[-i]
        if old_txt != ".":
            try: msg = await channel.fetch_message(mid) 
            except: 
                self.Data[f'{channelName}-MSGS'] = []
                await updatePlayer(self, pid)
                return
            #print(f'   |   Editing {channelName}')
            await msg.edit(content = ".")
            self.Data[f'{channelName}-MSGS'][-i] = [mid, "."]

async def updateData(self):
    channelName = 'game-info'
    if self.Refs['channels'].get(channelName) is None:         
        overwrites = {
            self.Refs['roles'][self.moderatorRole]: self.discord.PermissionOverwrite(read_messages=True),
            self.server.default_role: self.discord.PermissionOverwrite(read_messages=True)
        }
        channel = await self.server.create_text_channel(channelName, overwrites=overwrites, category= self.Refs['category']['Game-Data'])
        self.Refs['channels'][channelName] = channel
        print('   |   Added Channel:', channel.name)
    channel = self.Refs['channels'].get(channelName)
      
    maxToDisplay = 35
    ignoreKeys = ['PlayerData','Schedules','Queue','Queue-MSGS','RuleList',
                  'Schedule-Channel-MSGS','Suber-Votes-1','Suber-Votes-2',
                  'Suber-Votes-3','Suber-Votes-4','Suber-Votes-5','Subers',
                  'Suber-MSG','Votes','Mood','Array','lastAlive','NextTurnStartTime',
                  'CurrTurnStartTime']
    paramMap = {
        'TurnTime': 'Elasped Turn Time (sec)'
    }

    msgs = {}
    toSend = []
    for k in self.Data.keys():
        if k in ignoreKeys: continue
        if 'MSG' in k: continue
        val = self.Data[k]

        if isinstance(val, dict):  val = '```'+yaml.dump(self.Data[k])+'```'
        if isinstance(val, datetime.datetime): val = val - datetime.timedelta(seconds=val.second)

        name = str(k)
        if name in paramMap: name = paramMap[name]
        msgs[k]  = f"**{name}**:   {val}"
        
        for pid in self.Data['PlayerData'].keys():
            msgs[k] = msgs[k].replace(str(pid), self.Data['PlayerData'][pid]['Name']).replace('-05:51','')

    for k in sorted(msgs.keys()): toSend.append(msgs[k].strip())

    msgs = self.Data.get(f'{channelName}-MSGS')
    if msgs is None: msgs = []
    if len(msgs) != maxToDisplay:
        print(f'   |   Purging {channelName}-MSGS',  len(msgs))
        self.Data[f'{channelName}-MSGS'] = []
        await channel.purge()
        for i in range(maxToDisplay):
            msg = await channel.send(".")
            self.Data[f'{channelName}-MSGS'].append([msg.id, ""])
    
    msgs = self.Data.get(f'{channelName}-MSGS')
    for i in range(1,len(toSend)+1):
        mid, old_txt = msgs[-i]
        if old_txt != toSend[i-1]:
            try: msg = await channel.fetch_message(mid) 
            except: 
                self.Data[f'{channelName}-MSGS'] = []
                await updatePlayer(self, pid)
                return
            await msg.edit(content = toSend[i-1])
            self.Data[f'{channelName}-MSGS'][-i] = [mid, toSend[i-1]]

    for i in range(len(toSend)+1, maxToDisplay+1):
        mid, old_txt = msgs[-i]
        if old_txt != ".":
            try: msg = await channel.fetch_message(mid) 
            except: 
                self.Data[f'{channelName}-MSGS'] = []
                await updatePlayer(self, pid)
                return
            await msg.edit(content = ".")
            self.Data[f'{channelName}-MSGS'][-i] = [mid, "."]

 