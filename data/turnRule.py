#
#  Nomitron 4 Safe
#

async def endTurn(self, payload = None):
    if payload is not None and payload.get('Author') not in self.moderators: return

    print('   |   END OF TURN', self.Data['Turn'])
    await self.Refs['channels']['actions'].send(f"**End of Turn #{self.Data['Turn']}.**")

   
    await self.Mods.votingRule.bot_tally(self)
    await self.Mods.suberRule.suber_tally(self)
    await incrementTurn(self)
    


async def startTurn(self):
    print('   |   START OF TURN', self.Data['Turn'])
    await self.Refs['channels']['actions'].send(f"**Start of Turn #{self.Data['Turn']}.**")

    await self.Mods.suberRule.suberTick(self)
    await self.Mods.votingRule.popProposal(self)
    await self.Mods.suberRule.popSuber(self)
    await self.Mods.moodRule.checkEmotions(self)
    await self.Mods.coreMethods.rmJudge(self)
    await self.Mods.gladiatorRule.gladiatorPointCheck(self)
    await self.Mods.suitsRule.resetMethods(self)
    await self.Mods.clockMarket.stonks(self)
    

async def incrementTurn(self):
    dayStart = self.now()
    self.Data['VotingEnabled'] = False
    self.Data['Turn'] += 1
    self.Data['CurrTurnStartTime'] = self.now()
    self.Data['TurnTime'] = (self.now() - self.Data['CurrTurnStartTime']).total_seconds()

async def extendTurn(self, payload=None):
    if payload is not None: 
        if payload.get('Author') not in self.moderators: return
        await payload['raw'].channel.send('Turn extended 24 hrs. Use !tickTurn to manually trigger the next turn if needed')
    self.updateSchedule('End Of Turn', delta =  self.day )


async def reduceTurn(self, payload):
    if payload is not None: 
        if payload.get('Author') not in self.moderators: return
        await payload['raw'].channel.send('Turn reduced 24 hrs. Use !tickTurn to manually trigger the next turn if needed')
    self.updateSchedule('End Of Turn', delta =  -self.day )

async def update(self):
    self.Data['TurnTime'] = (self.now() - self.Data['CurrTurnStartTime']).total_seconds()
    