from time import sleep
import numpy
import asyncio

async def gom(self, payload):
    player = payload['raw'].author

    if self.Data['PlayerData'][player.id].get('Gom Jammer Test') not in [None, "Not Taken"]:
        await payload['raw'].channel.send("You have already taken the test this week.")
        return

    sleep(5)
    await payload['raw'].channel.send("Your test has begun.")
    starttime = self.now()
    self.Data['PlayerData'][player.id]['Gom Jammer Test'] = "In Progress"

    while self.now() - starttime < 15 * self.minute:
        await asyncio.sleep(20)
        for chan in self.Refs['channels'].values():
            async for lastMsg in chan.history(limit=50, after=starttime):
                if lastMsg.author.id != player.id: continue
                if lastMsg.created_at > starttime:
                    self.Data['PlayerData'][player.id]['Gom Jammer Test'] = "Failed"
                    print(lastMsg.content, lastMsg.created_at)
                    break
            if self.Data['PlayerData'][player.id]['Gom Jammer Test'] != "In Progress": break
        if     self.Data['PlayerData'][player.id]['Gom Jammer Test'] != "In Progress": break
    print('Endloop')
    if numpy.random.randint(1, 101, 1) > 85 or self.Data['PlayerData'][player.id]['Gom Jammer Test'] == "Failed":
        self.Data['PlayerData'][player.id]['Gom Jammer Test'] = "Failed"
        await payload['raw'].channel.send("Your test has ended. You have failed.")
        await self.Mods.emojiRule.addEmoji(self, player.id, '💉' )
        return
    if self.Data['PlayerData'][player.id]['Gom Jammer Test'] == "In Progress":
        self.Data['PlayerData'][player.id]['Gom Jammer Test'] = "Passed"
        await payload['raw'].channel.send("Your test has ended. You have passed.")
        await self.Mods.emojiRule.addEmoji(self, player.id, '🤸' )
        return
    

async def on_typing(self, payload):
    player = payload['user']
    if self.Data['PlayerData'][player.id].get('Gom Jammer Test') == "In Progress":
        self.Data['PlayerData'][player.id]['Gom Jammer Test'] = "Failed"
        print("Player is typing")
        return

async def resetGoms(self):
    for pid in self.Data['PlayerData'].keys():
        self.Data['PlayerData'][pid]['Gom Jammer Test'] = "Not Taken"
        await self.Mods.emojiRule.removeEmoji(self, pid, '💉' )
        await self.Mods.emojiRule.removeEmoji(self, pid, '🤸' )
    await self.Refs['channels']['actions'].send("-  Gom Jammer Reset.")

 