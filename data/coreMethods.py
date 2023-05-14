#
# Admin Module For Discord Bot
################################
import sys, os,datetime, discord, random, numpy
from pytube import YouTube
from shutil import copyfile
player = None

################################################
# Ping
async def ping(self, payload):
    await payload['raw'].channel.send('!pong')

################################################
# Echo text back
async def echo(self, payload):  
    if payload.get('Author') in self.moderators: await payload['raw'].channel.send(payload['Content'][6:])


################################################
# Player Commands
'''
async def stop(self, payload):
    global player
    print("   Stopping Player")
    if player is not None:
        tplayer = player
        tplayer.stop()
        player = None
        await tplayer.disconnect()
        os.remove(path+'music/tmp_music.mp3')
        os.remove(path+'music/tmp_music.mp4')

async def play(self, payload):
    # grab the user who sent the command
    global player
    print('   Starting Player')

    user=payload['raw'].author
    voice_channel=user.voice.channel
    channel=None

    yt = YouTube(text[0][1])
    video = yt.streams.filter(only_audio=True).first()    
    out_file = video.download(output_path=path+'music')
    
    base, ext = os.path.splitext(out_file)
    os.rename(out_file, path+'music/tmp_music'+ext)

    # only play music if user is in a voice channel
    if voice_channel != None:
        # grab user's voice channel
        channel=voice_channel.name
        # create StreamPlayer
        player = await voice_channel.connect()
        player.play(discord.FFmpegPCMAudio(path+'music/tmp_music'+ext))
    else:
        await print('User is not in a channel.')

async def update(self):
    global player
    if player is not None and not player.is_playing():
        await player.stop()
        await vc.disconnect()
        os.remove(self.path+'music/tmp_music.mp4')
        player = None
'''
################################################
# Clean Up Commands
async def clear(self, payload):
    if payload.get('Author') in self.moderators: 
        messages = [m async for m in payload['raw'].channel.history(limit=200)]
        for msg in messages: 
            try:await msg.delete()
            except: pass

################################################
# Mod Commands

async def player(self, payload):
    pid = payload['Author ID']

    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |   Setting Player For ',player.name)
        if self.Refs['players'][pid].get_role(self.Refs['roles']['Player'].id) is None:
            await self.Refs['players'][pid].add_roles( self.Refs['roles']['Player'])
            sys.exit(0)
       
async def sudo(self, payload):
    if payload.get('Author') in self.moderators: 
        await self.Refs['players'][payload['raw'].author.id].add_roles(self.Refs['roles'][self.moderatorRole])
    print('   Modded at', self.now()-self.Data['Time'])

async def sudont(self, payload):
    if payload.get('Author') in self.moderators:         
        await self.Refs['players'][payload['raw'].author.id].remove_roles(self.Refs['roles'][self.moderatorRole])
    
async def restart(self, payload):
    if payload.get('Author') in self.moderators:
        message = payload['raw']
        print('Restarting',payload.get('Author'))
        await message.channel.send('Going for Restart')
        print("Going For Restart...")
        sys.exit(0)

async def purge(self, payload):
    if payload.get('Author') in self.moderators:
        self.Data = {}
        await self.saveData()
        sys.exit(0)

async def judge(self, payload):
    pid = payload['Author ID']

    if payload.get('Author') in self.moderators and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await self.getPlayer(playerid, payload)
        pid = player.id
        print('   |   Setting Judge For ',player.name)
        if self.Refs['players'][pid].get_role(self.Refs['roles']['Judge'].id) is None:
            await self.Refs['players'][pid].add_roles(   self.Refs['roles']['Judge'])
            self.Data['Judge'] = pid
        else:
            await self.Refs['players'][pid].remove_roles(self.Refs['roles']['Judge'])
            self.Data['Judge'] = None

async def rmJudge(self):
    if self.Data.get('Judge') is not None:
        await self.Refs['players'][self.Data['Judge']].remove_roles(self.Refs['roles']['Judge'])
        self.Data['Judge'] = None

################################################
# On Message Commands
async def on_message(self, payload):
    message = payload['raw']
    botCharacter = '!'

    if payload['Content'] in ['!help', '! help']:
        with open('PlayerREADME.md', 'r') as helpFile:
            help = helpFile.readlines()
            msg = ""
            for line in help:
                if len(msg + line) > 1900:
                    await message.channel.send('```diff\n'+msg+'```')
                    msg = ""
                msg = msg + line
            if msg != "":
                await message.channel.send('```diff\n'+msg+'```')

    if payload['Content'] in [':heart:', '❤️']:
        await message.channel.send('❤️')
    
    if '?' in payload['Content'] and '!' == payload['Content'][0]:
        options = [
         "It is certain.",
         "It is decidedly so.",
         "Without a doubt.",
         "Yes definitely.",
         "You may rely on it.",
         "As I see it, yes.",
         "Most likely.",
         "Outlook good.",
         "Yes.",
         "Signs point to yes.",
         "Reply hazy, try again.",
         "Ask again later.",
         "Better not tell you now.",
         "Cannot predict now.",
         "Concentrate and ask again.",
         "Don't count on it.",
         "My reply is no.",
         "My sources say no.",
         "Outlook not so good.",
         "Very doubtful."]
        await message.channel.send(random.choice(options))

async def roll(self, payload):
    message = payload['raw']
    argv = payload['Content'].split(' ')
    diceInfo = argv[1].split('d')
    if len(diceInfo) == 2:
        randNum = numpy.random.randint(1, int(diceInfo[1])+1, int(diceInfo[0]))
        await message.channel.send(str(sum(randNum))+' : '+str(randNum).replace('  ',' ').replace(' ',', '))

async def nuke(self, payload):
    if payload.get('Author') not in self.moderators: return
    channel_name = payload['Channel']
    existing_channel = self.discord.utils.get(self.server.channels, name=channel_name)
    if existing_channel is not None:
        await existing_channel.clone(reason="Has been nuked")
        await existing_channel.delete()
    else:
        print(f'No channel named **{channel_name}** was found')