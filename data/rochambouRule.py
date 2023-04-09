#
#  Nomitron 4 Safe
#

# Commands
async def on_message(self, payload):
    cmd = payload['Content'].lower().strip()
    if cmd in ['!rock', '!paper','!scissors']:
        if payload['Channel'] == 'DM':
            self.Data['PlayerData'][payload['Author ID']]['Rock Paper Scissor Guess'] = cmd[1:]
            await payload['raw'].add_reaction('✔️')

        else: await payload['raw'].channel.send("You must DM me your resonse")

async def tally_RPS(self):
    scissors = []
    rock = []
    paper = []

    for pid in self.Data['PlayerData'].keys():
        if self.Data['PlayerData'][pid].get('Rock Paper Scissor Guess') == 'scissors':
            scissors.append(pid)
        if self.Data['PlayerData'][pid].get('Rock Paper Scissor Guess') == 'rock':
            scirockssors.append(pid)
        if self.Data['PlayerData'][pid].get('Rock Paper Scissor Guess') == 'paper':
            paper.append(pid)

        self.Data['PlayerData'][pid]['Rock Paper Scissor Guess'] = None

    msgs  =   "Rock :"+' '.join([self.Data['PlayerData'][p]['Name'] for p in rock])
    msgs += "\nPaper :"+' '.join([self.Data['PlayerData'][p]['Name'] for p in paper])
    msgs += "\nScissors :"+' '.join([self.Data['PlayerData'][p]['Name'] for p in scissors])
    await self.Refs['channels']['actions'].send(msgs)

    # Three Way Tie
    if len(scissors) == len(rock) and len(rock) == len(paper):
        await self.Refs['channels']['actions'].send("- Rock Paper Scissors: 3 Way TIE!")

    # 1+ is Empty
    elif len(scissors) == 0: await winners(self, paper,     '🧻')
    elif len(rock)     == 0: await winners(self, scissors,  '✂️')
    elif len(paper)    == 0: await winners(self, rock,      '🪨')
    
    elif (len(scissors) == 0 and len(rock) == 0 ) or \
         (len(rock) == 0     and len(paper) == 0 ) or \
         (len(paper) == 0    and len(scissors) == 0 ):
        await self.Refs['channels']['actions'].send("- Rock Paper Scissors: You all did the same group!")

    # All Populated
    else:
        # Scissors and Paper Minor
        if len(scissors) < len(rock) and len(paper) < len(rock):
            await winners(self, scissors,  '✂️')
        # Rock and Paper Minor
        if len(rock) < len(scissors) and len(paper) < len(scissors):
            await winners(self, paper,     '🧻')
        # Rock and Scissors Minor
        if len(rock) < len(paper)    and len(scissors) < len(paper):
            await winners(self, rock,      '🪨')

async def winners(self, p, k):
    if self.Data.get('Turn -3 RPS Winners') is not None:
        for ok,op in self.Data['Turn -3 RPS Winners']:
            for pid in op: await self.Mods.emojiRule.removeEmoji(self,pid,ok)
    self.Data['Turn -3 RPS Winners'] =  self.Data.get('Turn -2 RPS Winners')
    self.Data['Turn -2 RPS Winners'] =  self.Data.get('Turn -1 RPS Winners')
    self.Data['Turn -1 RPS Winners'] = {k:p}
    for pid in p: await self.Mods.emojiRule.addEmoji(self,pid,k)

    await self.Refs['channels']['actions'].send(f"- {k }WINS")
