import time, traceback, multiprocessing, re, yaml, socket, pytz
import sys, asyncio, os, importlib, glob, datetime, random, sys, datetime
from shutil import copyfile
from threading import Thread
import logging
from functools import reduce 
import operator

botCommandChar = '!'
path = "/usr/src/app/"
savefile = 'DiscordBot_Data.yml'

admin = 1057023272220373143 #'Crorem#6962 Sudo'

mainServerId  = 1028425604879634442
testServerId  = 1043621642938626171
moderatorRole = "Moderator"
playerRole    = "Player"
moderators  = ['Fenris#6136', 'Crorem#6962', 'iann39#8298', 'Alekosen#6969']
NonBotChannels = []
dontLogFunc = ['sudo', 'sudont','f','r','find','rule','ping']
hideLogFunc = ['rock','paper','scissors']
'''
Implement Modules By Placing Module Python File In Same Directory
Modules Must Have Different Names And Be Written With Python 3 Compatibility.
Use Blank.py as a Template for new modules.

It is recommended not to edit this file.
'''

class Object: pass
class DiscordNomicBot():

    """
    Initialize The Bot Handling Class  (Updated to Nomitron 4)
    """
    def __init__(self, ):
        print('='*50)
        print(f"Starting Nomitron 4\n",
              f"  System Time: {self.now()}\n",
              f"  Host: {socket.gethostname()}\n")

        # Storable Data
        self.Data = {   
            'lastAlive':0,
            'PlayerData' : {},
            'Schedules'  : {},
            'Turn': 0, 
            'Day': (self.now() - self.time(year = 2022, month=12, day = 1)).days, 
            'Time': self.now()
         }

        # Volatile Data
        self.Refs = {}
        self.Mods = Object()
        self.Tasks = set()
        self.server = None
        self.moduleNames = []
        self.NonBotChannels = NonBotChannels
        self.lastSaveTime= self.now() - datetime.timedelta(days=1)

        # Constants
        self.isholiday = False
        self.lock      = False
        self.second    = datetime.timedelta(seconds=1)
        self.minute    = 60 * self.second
        self.hour      = 60 * self.minute
        self.day       = 24 * self.hour
        self.week      = 7 * self.day

        self.path = "/usr/src/app/"
        self.savefile = savefile

        self.admin          = admin
        self.moderators     = moderators
        self.moderatorRole  = moderatorRole
        self.playerRole     = playerRole

        try:
            self.discord    = importlib.import_module('discord')
            #self.discord.utils.setup_logging(level=logging.ERROR, root=False)
            self.loop       = asyncio.new_event_loop()
            self.client     = self.discord.Client(loop = self.loop, heartbeat_timeout=60*10, intents=self.discord.Intents.all())
            self.clientid   = None
            self.token      = open(path+'token.secret','r').readlines()[0].strip()
            if self.token[-4:] != '_OL0': 
                print('   On Main Server')
                self.serverid = mainServerId
            else:                        
                print('   On Test Server')
                self.serverid = testServerId
            print("   Discord Version:", self.discord.__version__)
            print("   Using Token: ..." + self.token[-6:])
        except ImportError:
            print("Discord Library Not Found, install by \"pip install discord\"")
            sys.exit(0)

        try: os.mkdir(path + 'Backups/')
        except: pass

        # Import Modules
        print('   Importing Mods')
        for mod in glob.glob("*.py"):
            modName = mod[:-3]
            if mod in ['Blank.py', 'Nomitron.py']: continue
            print('      Importing Module:',modName)
            self.moduleNames.append(modName)
            setattr(self.Mods, modName, importlib.import_module(modName))


        @self.client.event
        async def on_ready(): await self.on_ready()

        @self.client.event
        async def on_message(message): await self.on_message(message)

        @self.client.event
        async def on_raw_reaction_add(reaction): await self.on_raw_reaction(reaction, 'add')

        @self.client.event
        async def on_raw_reaction_remove(reaction): await self.on_raw_reaction(reaction, 'remove')

        @self.client.event
        async def on_raw_typing(event): await self.on_raw_typing(event)

        self.client.run(self.token, reconnect=True, log_handler=None)


    """
    Updating/Creation of Data Structure
    """
    def updateData(self,):

        if 'Proposal#' not in self.Data:         self.Data['Proposal#']  = 300
        if 'Queue' not in self.Data:             self.Data['Queue']      = {}
        if 'Subers' not in self.Data:            self.Data['Subers']     = dict()
        for k in self.Data['Subers'].keys():
            for m in ['Assenter', 'Dissenter']:
                if isinstance(self.Data['Subers'][k][m]['DOB'], int):
                    self.Data['Subers'][k][m]['DOB'] = datetime.datetime.fromtimestamp(self.Data['Subers'][k][m]['DOB'], pytz.timezone('US/Central'))
            
        if 'Array' not in self.Data:             self.Data['Array']      = dict()
        if 'Mood' not in self.Data:              self.Data['Mood']       = None
        if 'DeckMSGs' not in self.Data:          self.Data['DeckMSGs']   = []


        dayStart = self.now()
        dayStart = self.time(dayStart.year, dayStart.month, dayStart.day)
        if 'CurrTurnStartTime' not in self.Data:    
            self.Data['CurrTurnStartTime'] = dayStart
        if 'NextTurnStartTime' not in self.Data:    
            self.Data['NextTurnStartTime'] = dayStart
        if 'Haymaker' not in self.Data:    
            self.Data['Haymaker'] = []
        if 'Old Matter Votes' not in self.Data:    
            self.Data['Old Matter Votes'] = {}
            
        if isinstance(self.Data['CurrTurnStartTime'], int):
            self.Data['CurrTurnStartTime'] = datetime.datetime.fromtimestamp(self.Data['CurrTurnStartTime'], pytz.timezone('US/Central'))
        
        if isinstance(self.Data['NextTurnStartTime'], int):
            self.Data['NextTurnStartTime'] = datetime.datetime.fromtimestamp(self.Data['NextTurnStartTime'], pytz.timezone('US/Central'))
        
        if isinstance(self.Data['CurrTurnStartTime'], float):
            self.Data['CurrTurnStartTime'] = datetime.datetime.fromtimestamp(self.Data['CurrTurnStartTime'], pytz.timezone('US/Central'))
        
        if isinstance(self.Data['NextTurnStartTime'], float):
            self.Data['NextTurnStartTime'] = datetime.datetime.fromtimestamp(self.Data['NextTurnStartTime'], pytz.timezone('US/Central'))

    
        if 'Gladiator' not in self.Data: 
            self.Data['Gladiator'] = {
                'Player': None, 
                'DOB':0
            }
        if 'Critic' not in self.Data:
            self.Data['Critic'] = {
                'Banned': [],
                'Opted In': [],
                'Starred':[]
            }
        if 'Wizard' not in self.Data:
            self.Data['Wizard'] = {
                'Time':self.now() - self.day, 
                'MSG': None
            }
        if isinstance(self.Data['Wizard']['Time'], int):
            self.Data['Wizard']['Time'] = datetime.datetime.fromtimestamp(self.Data['Wizard']['Time'], pytz.timezone('US/Central'))
        if isinstance(self.Data['Wizard']['Time'], float):
            self.Data['Wizard']['Time'] = datetime.datetime.fromtimestamp(self.Data['Wizard']['Time'], pytz.timezone('US/Central'))

    
        if 'Buddies' not in self.Data:
            self.Data['Buddies'] = {
                'Time Created': 1673244000, 
                'Buddies' : []
            }
        if 'Time Created' in self.Data['Buddies']:
            del self.Data['Buddies']['Time Created']
        if 'Emoji Recipes' in self.Data:
            del self.Data['Emoji Recipes']

        for pid, player in self.Refs['players'].items():
            name = player.name + "#" + str(player.discriminator)
            if self.Refs['roles'][playerRole] not in player.roles: continue

            if pid not in self.Data['PlayerData']: self.Data['PlayerData'][pid] = {}

            if 'Name' not in  self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['Name'] = name

            if 'Suits' not in  self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['Suits'] = None

            if self.Data['PlayerData'][pid].get('Nick') is None:
                self.Data['PlayerData'][pid]['Nick'] = self.Refs['players'][pid].nick
                if self.Data['PlayerData'][pid]['Nick'] is None:
                    self.Data['PlayerData'][pid]['Nick']= self.Refs['players'][pid].name

            if 'Proposal' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['Proposal'] = {}

            if 'File'       not in self.Data['PlayerData'][pid]['Proposal']:
                self.Data['PlayerData'][pid]['Proposal']['File'] = ''

            if 'Supporters' not in self.Data['PlayerData'][pid]['Proposal'] or type(self.Data['PlayerData'][pid]['Proposal']['Supporters']) is type(set()):
                self.Data['PlayerData'][pid]['Proposal']['Supporters'] = []



            if 'DOB'   not in self.Data['PlayerData'][pid]['Proposal']:
                self.Data['PlayerData'][pid]['Proposal']['DOB'] = self.now()
            
            if isinstance(self.Data['PlayerData'][pid]['Proposal']['DOB'], int):
                self.Data['PlayerData'][pid]['Proposal']['DOB'] = datetime.datetime.fromtimestamp(self.Data['PlayerData'][pid]['Proposal']['DOB'], pytz.timezone('US/Central'))
            if isinstance(self.Data['PlayerData'][pid]['Proposal']['DOB'], float):
                self.Data['PlayerData'][pid]['Proposal']['DOB'] = datetime.datetime.fromtimestamp(self.Data['PlayerData'][pid]['Proposal']['DOB'], pytz.timezone('US/Central'))



            if 'Color' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['Color'] = {'Hue':"None", "time": self.now() - self.day}

            if isinstance(self.Data['PlayerData'][pid]['Color']['time'], int):
                self.Data['PlayerData'][pid]['Color']['time'] = datetime.datetime.fromtimestamp(self.Data['PlayerData'][pid]['Color']['time'], pytz.timezone('US/Central'))
            if isinstance(self.Data['PlayerData'][pid]['Color']['time'], float):
                self.Data['PlayerData'][pid]['Color']['time'] = datetime.datetime.fromtimestamp(self.Data['PlayerData'][pid]['Color']['time'], pytz.timezone('US/Central'))

            

            if 'Friendship Tokens' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['Friendship Tokens'] = 0
        
            if 'Query' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['Query'] = None

            if "DI's" not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]["DI's"] = dict()

            if 'Inactive' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['Inactive'] = None

            if 'MoodGuess' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['MoodGuess'] = None

            if 'EmpathyCounter' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['EmpathyCounter'] = 0

            if 'InactiveWarned' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['InactiveWarned'] = False
            
            if 'Challanged' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['Challanged'] = False

            if 'Offers' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['Offers'] = 0

            if 'Emojis' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['Emojis'] = []

            if 'EmojiHold' not in self.Data['PlayerData'][pid]:
                self.Data['PlayerData'][pid]['EmojiHold'] = []

            if isinstance(self.Data['PlayerData'][pid]['Emojis'] , str):
                self.Data['PlayerData'][pid]['Emojis'] = list(self.Data['PlayerData'][pid]['Emojis'] )
        
        for pid in list(self.Data['PlayerData'].keys()):
            if pid not in self.Refs['players']:
                print('Delete', self.Data['PlayerData'][pid]['Name'])
                del self.Data['PlayerData'][pid]
        print('   Players In Game:',len(self.Data['PlayerData']))


    """
    Convert message data To Easier Message Payload. (Updated to Nomitron 4)
    """   
    def messageAsPayload(self, message):
        payload = {}

        if message == None:  return
        payload['raw'] = message

        payload['Author'] = message.author.name + "#" + str(message.author.discriminator)
        payload['Author ID'] = message.author.id
        payload['Channel Type'] = message.channel.type
        
        if payload['Channel Type'] in [self.discord.ChannelType.private, self.discord.ChannelType.group]:
            payload['Channel'] = "DM"
            payload['Category'] = "DM"
        else:
            payload['Channel'] = message.channel.name

        payload['Content'] = message.system_content.strip().replace('  ',' ')
        payload['Attachments'] = {}

        for file in message.attachments:  payload['Attachments'][file.filename] = file
        return payload


    """
    Pass a command to its respective module. (Updated to Nomitron 4)
    """   
    async def passToModule(self, function, payload= None, kwargs={}):
        targetFuncExists = False
        payload_tmp = []
        if payload is not None: payload_tmp = [dict(payload), ]
        if kwargs is None: kwargs = {}

        # Search For Duplicates Modules
        for name in self.moduleNames:
            mod = getattr(self.Mods, name)
            if hasattr(mod, function):
                targetFuncExists = True
        
        # If Not targeting a specific function
        if not targetFuncExists: 
            function = 'on_message'
            if payload_tmp is None: return

        # Send to all functions
        toDo = []
        for name in self.moduleNames:
            mod = getattr(self.Mods, name)
            if hasattr(mod, function):
                try:   toDo.append(getattr(mod, function)(self, *payload_tmp, **kwargs))
                except self.discord.errors.HTTPException: 
                    print(f'!!! HTTP Error In Module: {name} {function}!!!')
                except Exception as e: 
                    print(f'!!! Error In Module: {name} {function} {e}!!!')
                    raise e
        try:await asyncio.gather( *toDo )
        #except self.discord.errors.HTTPException: 
        #    print(f'!!! HTTP Error In Module: Gathering {function}!!!')
        except Exception as e: 
            print(f'!!! Error In Module: {function} {e}!!!')
            raise e

        


    """
    Settup Bot on Target Server (Updated to Nomitron 4)
    """
    async def on_ready(self):
        print()
        print('   Logged in as ' + self.client.user.name)
        self.clientid   = self.client.user.id

        for s in self.client.guilds:
            print( '      Found Server:',s.name)
            if s.id == self.serverid:
                self.server = s
                self.admin = self.server.owner.id
                print('   Joining Server')
        if self.server is None:
            print('   Server not found!!!')
            sys.exit(0)

        self.Refs['channels'] = {}
        self.Refs['category'] = {}
        self.Refs['players']  = {}
        self.Refs['roles']    = {}

        for role in await self.server.fetch_roles():
            self.Refs['roles'][role.name] = role
        for member in self.Refs['roles'][self.playerRole].members:
            self.Refs['players'][member.id] = member
        for channel in await self.server.fetch_channels():
            if str(channel.type) == 'category':  self.Refs['category'][channel.name]= channel
            else:                                self.Refs['channels'][channel.name]= channel
            print('      Found Channel:', channel.name)



        #######################################################################
        # Create Channels For Game State
        #
        print("      Creating Channel Map")
        if self.Refs['category'].get("Game-Data") is None:
            print('   Adding Game-Data Category')
            category = await self.server.create_category("Game-Data")
            self.Refs['category']['Game-Data']= channel

        print('      Loading Data')
        await self.loadData()
        await self.passToModule('setup')
        print('   Setup Finished!')

        #for chan in self.Refs['channels'].keys():
        #    async for msg in self.Refs['channels'][chan].history(after = self.Data['lastAlive']):
        #        await self.on_message(msg)

        while 1:
            self.Data['lastAlive'] = datetime.datetime.now()

            startTime = self.now()
            while self.now() - startTime < self.minute:
                await self.checkSchedule()
                await asyncio.sleep(5)
                self.Data['Time'] = self.now()

            
            try: await self.passToModule('update')
            except Exception as e: print('ERROR:', e)
            try:await self.runTasks()
            except Exception as e: print('ERROR:', e)
            await self.saveData()
        print('Exit of Loop')


    """
    Handle Message Event (Updated to Nomitron 4)
    """
    async def on_message(self, message):
        if message.author.id == self.client.user.id: return
        if self.Refs['players'].get(message.author.id) is None: return
        if self.Refs['players'][message.author.id].get_role(self.Refs['roles'][self.playerRole].id) is None: return

        payload = self.messageAsPayload(message)
        if payload['Channel'] in self.NonBotChannels: return

        found = None
        if self.isholiday and payload.get('Author') not in self.moderators: return
        while self.lock: await asyncio.sleep(1)
        if len(payload['Content']) > 0 and payload['Content'][0][0] == botCommandChar:
            print('   MSG--', payload['Content'], '-----')
            functionName = payload['Content'][1:].split(' ')[0]
            await self.passToModule(functionName, payload)
            await self.runTasks()
            if functionName in hideLogFunc:
                await self.send(self.Refs['channels'].get('actions-log'), f"{payload['Author']} - || {payload['Content']}\n ;) ||")
            
            elif functionName not in dontLogFunc:
                await self.send(self.Refs['channels'].get('actions-log'), f"{payload['Author']} - {payload['Content']}")
            print('   --------------------------------')
        elif len(payload['Content']) > 0 or len(payload['Attachments']) > 0:
            await self.passToModule('on_message', payload)
            await self.runTasks()
        
        await self.saveData()


    """
    Handle Reactions (Updated to Nomitron 4)
    """
    async def on_raw_reaction(self, payload, mode):
        if payload.user_id == self.client.user.id: return
        if self.Refs['players'].get(payload.user_id) is None: return
        if self.Refs['players'][payload.user_id].get_role(self.Refs['roles'][self.playerRole].id) is None: return

        user = self.Refs['players'][payload.user_id]
        msg = None
        channel = self.client.get_channel(payload.channel_id)
        if channel is None:  msg = await    user.fetch_message(payload.message_id)
        else:                msg = await channel.fetch_message(payload.message_id)


        # Create Payload
        react_payload = self.messageAsPayload(msg)
        react_payload['msg']     = msg
        react_payload['message'] = msg
        react_payload['raw']     = payload
        react_payload['mode']    = mode
        react_payload['user']    = user
        react_payload['emoji']   = str(payload.emoji.name)
        react_payload['name']    = user.name + '#' + user.discriminator
    

        if self.isholiday: return

        while self.lock: await asyncio.sleep(1)
        await self.passToModule('on_reaction', react_payload)

        if mode == 'add' and str(payload.emoji) == str('🔄') and react_payload['name'] in self.moderators: 
            await msg.remove_reaction(str('🔄'), user)
            await self.on_message(msg)

        await self.saveData()


    """
    Member Greeting And Initialization  (Updated to Nomitron 4)
    """
    async def on_member_join(self, member):
        await self.passToModule('on_member_join', member)
        await self.saveData()
        print("Going For Restart...")
        sys.exit(0)


    """
    Member typing start (Updated to Nomitron 4)
    """
    async def on_raw_typing(self, payload):
        if payload.user_id == self.client.user.id: return
        if self.serverid != payload.guild_id: return
        if self.Refs['players'].get(payload.user_id) is None: return
        if self.Refs['players'][payload.user_id].get_role(self.Refs['roles'][self.playerRole].id) is None: return

        user    = self.Refs['players'][payload.user_id]
        channel = self.client.get_channel(payload.channel_id)
        start   = payload.timestamp
        if channel is None:  return
       
        # Create Payload
        typingPayload = {}
        typingPayload['time']    = start
        typingPayload['raw']     = payload
        typingPayload['Channel'] = channel
        typingPayload['user']    = user
        typingPayload['name']    = user.name + '#' + user.discriminator

        await self.passToModule('on_typing', typingPayload)
        await self.saveData()

    """
    Save Memory Data From File (Updated to Nomitron 4)
    """
    async def saveData(self):
        #print('   -----SAVING-----')
        self.Data['lastAlive'] = datetime.datetime.now()
        if self.now() - self.lastSaveTime > datetime.timedelta(minutes=10):
            if os.path.isfile(path + savefile): copyfile(path + savefile, path + 'Backups/'+ savefile + '-' + str(datetime.datetime.now()))
            self.lastSaveTime = self.now()
        with open(path + savefile, 'w') as handle: yaml.dump(self.Data, handle)

        list_of_files = glob.glob(path + 'Backups/*')
        sorted(list_of_files, key=os.path.basename)
        for full_path in list_of_files[max([1000 - len(list_of_files), -1]): ]:
            os.remove(full_path)
        

    """
    Load Memory Data From File (Updated to Nomitron 4)
    """
    async def loadData(self):
        list_of_files = glob.glob(path + 'Backups/*')
        sorted(list_of_files, key=os.path.basename)
        newData = None
        if os.path.isfile(path + savefile):
            with open(path + savefile, 'r') as handle:
                newData = yaml.safe_load(handle)
       
        for i in range(len(list_of_files)):
            if newData is not None: break
            with open(list_of_files[-1 - i], 'r') as handle: newData = yaml.safe_load(handle)
            print('   LOADING FROM BACKUP', list_of_files[-1 - i])
        if newData is None: 
            with open(path + savefile, 'w') as handle: yaml.dump(self.Data, handle)
            self.Data['lastAlive'] = datetime.datetime.now()
        else:
            for k in self.Data.keys(): 
                if k not in newData: newData[k] = self.Data[k]
            self.Data = dict(newData)

        self.updateData()
        await self.saveData()


    """
    DM a player (Updated to Nomitron 4)
    """
    async def dm(self,pid,msg):
        if isinstance(pid, int): player = self.Refs['players'][pid]
        else:                    player = pid
       
        try:     return await player.send(msg)
        except:  print('Failed to DM', player.name)


    """
    Send Long Messages to a channel.
    """
    async def send(self, target, content):
        if target is None: return
        isDM = isinstance(target, self.discord.User) or isinstance(target, self.discord.Member)
        msg = ""
        for line in content.split('\n'):
            line += '\n'
            if len(msg + line) > 1900:
                if isDM: await self.dm(target, msg)
                else:    await target.send(msg)

                while len(line) > 1900:
                    msgend = line[1900:].index(' ')
                    if isDM: await self.dm(target, line[:1900+msgend])
                    else:    await target.send(line[:1900+msgend])
                    line = line[1900+msgend:]
                msg = line
            else: msg += line
        if len(msg) > 0: 
            if isDM: await self.dm(target, msg)
            else:    await target.send(msg)


    """
    Get Data variable to Value
    """
    def getFromDict(self, keys):
        if not isinstance(keys, list): keys = [keys,]
        return reduce(operator.getitem, keys, self.Data)


    """
    Set Data variable to Value
    """
    async def set_data(self, keys, value):
        print('   |   - setting', keys)
        if isinstance(keys, list):
            self.getFromDict(keys[:-1])[keys[-1]] = value
        else:    self.Data[keys] = value


    """
    Schedule Event (Updated to Nomitron 4)
    """
    def schedule(self,name,function, parameter, nextTime, interval, varis=None):
        if name in self.Data['Schedules']: 
            print(f'      Schedule {name} Exists: Skipping...')
            return 
        else:
            if isinstance(function, str): funcName = function
            else: funcName = str(function.__name__)
            if isinstance(nextTime, datetime.datetime):
                interval = interval.total_seconds()
            self.Data['Schedules'][name] = {
                'nextTime'  : nextTime,
                'interval'  : interval,
                'parameter' : parameter,
                'function'  : funcName,
                'variables' : varis
            }


    """
    Update Schedule Event (Updated to Nomitron 4)
    """
    def updateSchedule(self,name, nextTime = None, delta = None, interval = None):
        if name not in self.Data['Schedules']: 
            print(f'   |   Schedule {name} Doesnt Exist: Skipping...')
            return 
        else:
            print(f'   |   Updating Schedule {name}', nextTime, delta, interval)
            if nextTime is not None:
                self.Data['Schedules'][name]['nextTime'] = nextTime
            elif delta is not None:
                self.Data['Schedules'][name]['nextTime'] += delta
            elif interval is not None:
                if isinstance(self.Data['Schedules'][name]['nextTime'], datetime.datetime):
                    dNextTime = -datetime.timedelta(seconds=self.Data['Schedules'][name]['interval']) + interval
                    self.Data['Schedules'][name]['nextTime'] += dNextTime
                    self.Data['Schedules'][name]['interval'] = interval.total_seconds()
                else: 
                    dNextTime = -self.Data['Schedules'][name]['interval'] + interval
                    self.Data['Schedules'][name]['nextTime'] += dNextTime
                    self.Data['Schedules'][name]['interval'] = interval
                
                
    """
    Scheduler Check Process (Updated to Nomitron 4)
    """
    async def checkSchedule(self):
        toDo = []
        toDoNames = []
        for sched in list(self.Data['Schedules'].keys()):
            paramKey = self.Data['Schedules'][sched]['parameter']
            parameter = self.Data
            
            # Get schedule parameter value
            if isinstance(paramKey,list):
                for k in paramKey: 
                    parameter = parameter.get(k)
                    # Bad Path Check
                    if parameter is None:
                        print('Bad Schedule Key: Removing', sched)
                        del self.Data['Schedules'][sched]
                        continue
            else: parameter = parameter.get(paramKey)

            # If Schedule To Be Executed
            if parameter >= self.Data['Schedules'][sched]['nextTime']:
                if self.isholiday:
                    if isinstance(parameter, datetime.datetime):
                        if sched in ['End Of Day','End Of Turn']:
                            self.Data['Schedules'][sched]['nextTime'] += self.day
                            continue

                # Run Event
                toDoNames.append(sched)
                kwargs = self.Data['Schedules'][sched].get('variables')
                toDo.append(self.passToModule(self.Data['Schedules'][sched]['function'], kwargs = kwargs))

                # Re-Schedule or Close Schedule
                interval = self.Data['Schedules'][sched]['interval']
                if interval is None:
                    del self.Data['Schedules'][sched]
                    continue
                elif isinstance(self.Data['Schedules'][sched]['nextTime'], datetime.datetime):
                    interval = datetime.timedelta(seconds=interval)
                self.Data['Schedules'][sched]['nextTime'] += interval
        if len(toDoNames) > 0: print('   Scheduler:-----------')
        for i in toDoNames: print('   |  ',i)
        if len(toDoNames) > 0: print('   ---------------------')
        self.lock = True
        await asyncio.gather( *toDo )
        await self.runTasks()
        if len(toDoNames) > 0: print('   ---------------------')
        self.lock = False


    """
    Run Tasks Sent By Mods (Updated to Nomitron 4)
    """
    async def runTasks(self):
        if len(self.Tasks) == 0: return
        print('   ----------------------------------')
        print('   |   Run Tasks: ')
        toDo = list(self.Tasks)
        self.Tasks = set()
        await asyncio.gather( *toDo )
        self.Data['lastAlive'] = datetime.datetime.now()
        if len(self.Tasks) > 0: await self.runTasks()
        print('   ----------------------------------')
        await self.saveData()


    """
    Get Datetime (Updated to Nomitron 4)
    """
    def time(self, *args, **kwargs):
        return datetime.datetime(*args,**kwargs,tzinfo = pytz.timezone('Etc/GMT+6'))


    """
    Get Now (Updated to Nomitron 4)
    """
    def now(self,):

        t = datetime.datetime.now(pytz.timezone('Etc/GMT+6'))
        t = self.time(t.year, t.month, t.day, t.hour, t.minute, t.second)
        return t


    """
    Get Player From Mention (Updated to Nomitron 4)
    """
    async def getPlayer(self, playerid, payload):
        if len(playerid) == 0: return None
        else:
            player = self.server.get_member(int(re.search(r'\d+', playerid).group()))
            if player is not None: return player
            else: await payload['raw'].channel.send('Player with id, ' + playerid + ' cannot be found.')
        return None

print('\n\n')
bot = DiscordNomicBot()
