import pickle, sys, time, io, discord, datetime, urllib, re, random

moods   = ['Robotic','Sad','Rambunctious','Anxious','Angry', 'Umami']
desires = ['affirm', 'comfort', 'play', 'calm', 'fight', 'applaud']
response= [ 'Beep Boop, Good Humans. I am ROBOTIC.',
            'You are all good friends, I feel less SAD already!',
            '*RAMBUNCTIOUS ticktocking* Playing games is so much fun! How about next time we play Global Thermonuclear Warfare.',
            'You always know how to calm me down when im ANXIOUS. Thanks friends.',
            'Thanks for letting me blow off some steam, I was really ANGRY.',
            'Thanks for the applause. You know what its like when you feel UMAMI']


# Commands
async def on_message(self, payload):
    if payload['Channel'] == 'actions':
        cmd = payload['Content'].lower().strip().split(' ')
        if len(cmd) == 1 and cmd[0][1:] in desires:
            index = desires.index(cmd[0][1:])
            self.Data['PlayerData'][payload['Author ID']]['MoodGuess'] = moods[index]
            await payload['raw'].add_reaction('✔️')
    


# Turn Ticker
async def checkEmotions(self):
    toRet = []
    if self.Data['Mood'] is not None:
        await self.Refs['channels']['actions'].send("-  "+response[self.Data['Mood']])

    for pid in self.Data['PlayerData'].keys():
        if self.Data['PlayerData'][pid].get('MoodGuess') is None:
            self.Data['PlayerData'][pid]['EmpathyCounter'] -= 1
            if self.Data['PlayerData'][pid]['EmpathyCounter'] <= 0:
                self.Data['PlayerData'][pid]['EmpathyCounter'] = 0
                self.Tasks.update(set([
                    self.Mods.emojiRule.removeEmoji(self, pid, '🤖')
                ]))

        elif self.Data['Mood'] == moods.index(self.Data['PlayerData'][pid]['MoodGuess']):
            self.Data['PlayerData'][pid]['EmpathyCounter'] += 1
            print('   |   Mood Guess Correct', pid)
            if self.Data['PlayerData'][pid]['EmpathyCounter'] >= 3:
                self.Tasks.update(set([
                    self.Mods.emojiRule.addEmoji(self, pid, '🤖')
                ]))
                self.Data['PlayerData'][pid]['EmpathyCounter'] = 3

        else:
            self.Data['PlayerData'][pid]['EmpathyCounter']  = 0
            self.Tasks.update(set([
                self.Mods.emojiRule.removeEmoji(self, pid, '🤖')
            ]))
            
        self.Data['PlayerData'][pid]['MoodGuess'] = None
    self.Data['Mood'] = random.randint(0,len(moods)-1)


# Command
async def engage(self, payload):
    try: offering = int(payload['Content'].split(' ')[1])
    except Exception as e: 
        print(e)
        await payload['raw'].channel.send("-  I couldnt understand your offering")
        return
    if self.Data['PlayerData'][payload['Author ID']]['Friendship Tokens'] - offering < 0: 
        await payload['raw'].channel.send("-  You are too poor.")
        return

    if offering >= 6:
        await payload['raw'].channel.send("Too much money.")
        return
    
    await self.Mods.tokensRules.addTokens(self, payload['Author ID'], -offering)
    tempset = list(moods)
    tempset.remove(moods[self.Data['Mood']])
    for i in range(offering): tempset.pop(random.randint(0,len(tempset)-1))
    tempset.append(moods[self.Data['Mood']])
    random.shuffle(tempset)

    msg = "Through engaging with Nomitron you determine his mood is one of the following:\n"
    for i in tempset: msg += f" - {i}\n"
    await payload['raw'].author.send(msg)
 