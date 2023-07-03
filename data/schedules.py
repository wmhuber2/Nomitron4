#
#  Nomitron 4 Safe
#

import datetime
days = ['Mon','Tues','Wed','Thr','Fri','Sat','Sun']
async def setup(self):
    print('   Creating Schedules:')
    dayStart = self.now()
    dayStart = self.time(dayStart.year, dayStart.month, dayStart.day)

    self.schedule(
        name = 'End Of Day', 
        function = onDayEnd, 
        parameter = 'Time',
        nextTime = dayStart + self.day,
        interval = self.day
    )

    self.schedule(
        name = 'Start Of Day', 
        function = onDayStart, 
        parameter = 'Day',
        nextTime = self.Data['Day'] +1,
        interval = 1
    )

    self.schedule(
        name = 'End Of Turn', 
        function = self.Mods.turnRule.endTurn, 
        parameter = 'Time',
        nextTime = dayStart + self.day,
        interval = self.day
    )

    self.schedule(
        name = 'Start Of Turn', 
        function = self.Mods.turnRule.startTurn, 
        parameter = 'Turn',
        nextTime = self.Data['Turn'] +1,
        interval = 1
    )

    criticStart = self.time(dayStart.year, dayStart.month, 6)
    while criticStart + self.week < self.now():  criticStart += self.week
    self.schedule(
        name = 'New Critic', 
        function = self.Mods.criticRule.getNewCritic, 
        parameter = 'Time',
        nextTime = criticStart + self.week,
        interval = self.week
    )

    gladStart = self.time(dayStart.year, dayStart.month, 6)
    while gladStart + self.week < self.now():  gladStart += self.week
    self.schedule(
        name = 'Reset Gladiator', 
        function = self.Mods.gladiatorRule.resetChallenges, 
        parameter = 'Time',
        nextTime = gladStart + self.week,
        interval = self.week
    )
    
    budStart = self.time(dayStart.year, dayStart.month, 6)
    while budStart + self.week < self.now():  budStart += self.week
    self.schedule(
        name = 'Reset Buddies', 
        function = self.Mods.buddyRule.buddify, 
        parameter = 'Time',
        nextTime = budStart + self.week,
        interval = self.week
    )

    traderStart = self.time(dayStart.year, dayStart.month, 6)
    while traderStart + self.week < self.now():  traderStart += self.week
    self.schedule(
        name = 'Reset Trader', 
        function = self.Mods.traderRule.resetTraderWeek, 
        parameter = 'Time',
        nextTime = traderStart + self.week,
        interval = self.week
    )

    gomStart = self.time(dayStart.year, dayStart.month, 6)
    while gomStart + self.week < self.now():  gomStart += self.week
    self.schedule(
        name = 'Reset Gom Jammer', 
        function = self.Mods.gomJammerRule.resetGoms, 
        parameter = 'Time',
        nextTime = gomStart + self.week,
        interval = self.week
    )

    matterStart = self.time(dayStart.year, dayStart.month, 6)
    while matterStart + self.week < self.now():  matterStart += self.week
    self.schedule(
        name = 'Reset Matter Baby', 
        function = self.Mods.matterRule.tallyMatter, 
        parameter = 'Time',
        nextTime = matterStart + self.week,
        interval = self.week
    )

    radioStart = self.time(dayStart.year, dayStart.month, 6)
    while radioStart + self.hour < self.now():  radioStart += self.hour
    self.schedule(
        name = 'Radioactive Tick', 
        function = self.Mods.radioactiveRule.radioactiveTick, 
        parameter = 'Time',
        nextTime = radioStart + self.hour,
        interval = self.hour
    )
    
    horseStart = self.time(dayStart.year, dayStart.month, 6, 12)
    while horseStart + self.day < self.now():  horseStart += self.day
    self.schedule(
        name = 'Horse Newsletter', 
        function = self.Mods.horseRule.randHorse, 
        parameter = 'Time',
        nextTime = horseStart + self.day,
        interval = self.day
    )

async def onDayEnd(self):
    print('   |   END OF DAY', self.Data['Day'])
    await incrementDay(self)
    try: await self.Mods.horseRule.checkHorses(self)
    except: print('Horse Error')
    try: await self.Refs['channels']['mod-spam'].send(file=self.discord.File(self.path + self.savefile))
    except: pass
    await self.Mods.rules.updateRules(self)

async def onDayStart(self):
    print('   |   START OF DAY', self.Data['Day'])
    await self.Refs['channels']['actions'].send(f"-  The Day is Now: {days[self.Data['Time'].weekday()]} Day {self.Data['Day']}")
    

async def incrementDay(self):
    self.Data['Day'] += 1

async def setDay(self, payload):
    print('   |  Setting Nick')
    day = int(payload['Content'].split(' ')[-1])
    await payload['raw'].add_reaction('✔️')
    
    for sched in list(self.Data['Schedules'].keys()):
        if 'Day' == self.Data['Schedules'][sched]['parameter'] or 'Day' in self.Data['Schedules'][sched]['parameter']:
            self.Data['Schedules'][sched]['nextTime'] += day - self.Data['Day']
    self.Data['Day'] = day

async def holiday(self, payload):
    if payload.get('Author') not in self.moderators: return

    self.isholiday = self.isholiday and False

    if self.isholiday: await self.Refs['channels']['actions'].send(f"-  It is now a holiday.")
    else:              await self.Refs['channels']['actions'].send(f"-  It is no longer a holiday.")
    

