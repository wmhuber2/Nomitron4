import numpy as np

async def giveRadioactive(self, payload):
    for pid in self.Data['PlayerData'].keys():
        await self.Mods.emojiRule.addEmoji(self, pid, '☢️' )

async def radioactiveTick(self):
    for pid in self.Data['PlayerData'].keys():
        if np.random.randint(1, 2001, 1) == 1:
            await self.Mods.emojiRule.removeEmoji(self, pid, '☢️' )

        