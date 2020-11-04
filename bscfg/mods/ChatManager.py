# -*- coding: utf8 -*-
import bs
import bsInternal
import datetime
import time
import os.path
import some
from thread import start_new_thread
import handle
import subprocess
import random

try:
    from googletrans import Translator
    _googletrans = True
except:
    print 'googletrans not present'
    _googletrans = False

if not some.translator: _googletrans = False
import json

try:
    from profanity import profanity
    _profanity = True
except:
    print 'profanity not present'
    _profanity = False

import chatCmd
import DB_Manager as db

supported_langs = ['it', 'fr', 'es', 'de', 'ru', 'hi', 'ta', 'ur', 'ar']

timeouts = {
    '/heal': 30,
    '/me': 10,
    '/list': 20,
    '/help': 20,
    '/shop': 20,
    '/bet': 30,
    '/sm': 300,
    '/beg': 30
}

last = {}
cmds = []
mutedIDs = []
filter_words =                                                                                                                                         ['2g1c', '2 girls 1 cup', 'acrotomophilia', 'alabama hot pocket', 'alaskan pipeline', 'anal', 'anilingus', 'anus', 'apeshit', 'arsehole', 'ass', 'asshole', 'assmunch', 'auto erotic', 'autoerotic', 'babeland', 'baby batter', 'baby juice', 'ball gag', 'ball gravy', 'ball kicking', 'ball licking', 'ball sack', 'ball sucking', 'bangbros', 'bareback', 'barely legal', 'barenaked', 'bastard', 'bastardo', 'bastinado', 'bbw', 'bdsm', 'beaner', 'beaners', 'beaver cleaver', 'beaver lips', 'bestiality', 'big black', 'big breasts', 'big knockers', 'big tits', 'bimbos', 'birdlock', 'bitch', 'bitches', 'black cock', 'blonde action', 'blonde on blonde action', 'blowjob', 'blow job', 'blow your load', 'blue waffle', 'blumpkin', 'bollocks', 'bondage', 'boner', 'boob', 'boobs', 'booty call', 'brown showers', 'brunette action', 'bukkake', 'bulldyke', 'bullet vibe', 'bullshit', 'bung hole', 'bunghole', 'busty', 'butt', 'buttcheeks', 'butthole', 'camel toe', 'camgirl', 'camslut', 'camwhore', 'carpet muncher', 'carpetmuncher', 'chocolate rosebuds', 'circlejerk', 'cleveland steamer', 'clit', 'clitoris', 'clover clamps', 'clusterfuck', 'cock', 'cocks', 'coprolagnia', 'coprophilia', 'cornhole', 'coon', 'coons', 'creampie', 'cum', 'cumming', 'cunnilingus', 'cunt', 'darkie', 'date rape', 'daterape', 'deep throat', 'deepthroat', 'dendrophilia', 'dick', 'dildo', 'dingleberry', 'dingleberries', 'dirty pillows', 'dirty sanchez', 'doggie style', 'doggiestyle', 'doggy style', 'doggystyle', 'dog style', 'dolcett', 'domination', 'dominatrix', 'dommes', 'donkey punch', 'double dong', 'double penetration', 'dp action', 'dry hump', 'dvda', 'eat my ass', 'ecchi', 'ejaculation', 'erotic', 'erotism', 'escort', 'eunuch', 'faggot', 'fecal', 'felch', 'fellatio', 'feltch', 'female squirting', 'femdom', 'figging', 'fingerbang', 'fingering', 'fisting', 'foot fetish', 'footjob', 'frotting', 'fuck', 'fuck buttons', 'fuckin', 'fucking', 'fucktards', 'fudge packer', 'fudgepacker', 'futanari', 'gang bang', 'gay sex', 'genitals', 'giant cock', 'girl on', 'girl on top', 'girls gone wild', 'goatcx', 'goatse', 'god damn', 'gokkun', 'golden shower', 'goodpoop', 'goo girl', 'goregasm', 'grope', 'group sex', 'g-spot', 'guro', 'hand job', 'handjob', 'hard core', 'hardcore', 'hentai', 'homoerotic', 'honkey', 'hooker', 'hot carl', 'hot chick', 'how to kill', 'how to murder', 'huge fat', 'humping', 'incest', 'intercourse', 'jack off', 'jail bait', 'jailbait', 'jelly donut', 'jerk off', 'jigaboo', 'jiggaboo', 'jiggerboo', 'jizz', 'juggs', 'kike', 'kinbaku', 'kinkster', 'kinky', 'knobbing', 'leather restraint', 'leather straight jacket', 'lemon party', 'lolita', 'lovemaking', 'make me come', 'male squirting', 'masturbate', 'menage a trois', 'milf', 'missionary position', 'motherfucker', 'mound of venus', 'mr hands', 'muff diver', 'muffdiving', 'nambla', 'nawashi', 'negro', 'neonazi', 'nigga', 'nigger', 'nig nog', 'nimphomania', 'nipple', 'nipples', 'nsfw images', 'nude', 'nudity', 'nympho', 'nymphomania', 'octopussy', 'omorashi', 'one cup two girls', 'one guy one jar', 'orgasm', 'orgy', 'paedophile', 'paki', 'panties', 'panty', 'pedobear', 'pedophile', 'pegging', 'penis', 'phone sex', 'piece of shit', 'pissing', 'piss pig', 'pisspig', 'playboy', 'pleasure chest', 'pole smoker', 'ponyplay', 'poof', 'poon', 'poontang', 'punany', 'poop chute', 'poopchute', 'porn', 'porno', 'pornography', 'prince albert piercing', 'pthc', 'pubes', 'pussy', 'queaf', 'queef', 'quim', 'raghead', 'raging boner', 'rape', 'raping', 'rapist', 'rectum', 'reverse cowgirl', 'rimjob', 'rimming', 'rosy palm', 'rosy palm and her 5 sisters', 'rusty trombone', 'sadism', 'santorum', 'scat', 'schlong', 'scissoring', 'semen', 'sex', 'sexo', 'sexy', 'shaved beaver', 'shaved pussy', 'shemale', 'shibari', 'shit', 'shitblimp', 'shitty', 'shota', 'shrimping', 'skeet', 'slanteye', 'slut', 's&m', 'smut', 'snatch', 'snowballing', 'sodomize', 'sodomy', 'spic', 'splooge', 'splooge moose', 'spooge', 'spread legs', 'spunk', 'strap on', 'strapon', 'strappado', 'strip club', 'style doggy', 'suck', 'sucks', 'suicide girls', 'sultry women', 'swastika', 'swinger', 'tainted love', 'taste my', 'tea bagging', 'threesome', 'throating', 'tied up', 'tight white', 'tit', 'tits', 'titties', 'titty', 'tongue in a', 'topless', 'tosser', 'towelhead', 'tranny', 'tribadism', 'tub girl', 'tubgirl', 'tushy', 'twat', 'twink', 'twinkie', 'two girls one cup', 'undressing', 'upskirt', 'urethra play', 'urophilia', 'vagina', 'venus mound', 'vibrator', 'violet wand', 'vorarephilia', 'voyeur', 'vulva', 'wank', 'wetback', 'wet dream', 'white power', 'wrapping men', 'wrinkled starfish', 'xxx', 'yaoi', 'yellow showers', 'yiffy', 'zoophilia', '🖕', 'aand', 'aandu', 'balatkar', 'beti chod', 'bhadva', 'bhadve', 'bhandve', 'bhootni ke', 'bhosad', 'bhosadi ke', 'boobe', 'chakke', 'chinaal', 'chinki', 'chod', 'chodu', 'chodu bhagat', 'chooche', 'choochi', 'choot', 'choot ke baal', 'chootia', 'chootiya', 'chuche', 'chuchi', 'chudai khanaa', 'chudan chudai', 'chut', 'chut ke baal', 'chut ke dhakkan', 'chut maarli', 'chutad', 'chutadd', 'chutan', 'chutia', 'chutiya', 'gaand', 'gaandfat', 'gaandmasti', 'gaandufad', 'gandu', 'gashti', 'gasti', 'ghassa', 'ghasti', 'harami', 'haramzade', 'hawas', 'hawas ke pujari', 'hijda', 'hijra', 'jhant', 'jhant chaatu', 'jhant ke baal', 'jhantu', 'kamine', 'kaminey', 'kanjar', 'kutta', 'kutta kamina', 'kutte ki aulad', 'kutte ki jat', 'kuttiya', 'loda', 'lode', 'lavde', 'lauda', 'lodu', 'lund', 'lund choos', 'lund khajoor', 'lundtopi', 'lundure', 'maa ki chut', 'maal', 'madar chod', 'mooh mein le', 'mutth', 'najayaz', 'najayaz aulaad', 'najayaz paidaish', 'paki', 'pataka', 'patakha', 'raand', 'randi', 'saala', 'saala kutta', 'saali kutti', 'saali randi', 'suar', 'suar ki aulad', 'tatte', 'tatti', 'teri maa ka bhosada', 'teri maa ka boba chusu', 'teri maa ki chut', 'tharak', 'tharki', 'madarchod', 'lawde', 'lawda',]
filter_words.extend([
    x.lower() for x in open(some.badfile).read().split('\n') if x != ''
])

if _profanity:
    profanity.load_words(filter_words)
if _googletrans:
    translator = Translator()


def chatCmd_loop():
    global cmds
    if cmds:
        for v in cmds:
            chatCmd.cmd(v)
        cmds = []
    with bs.Context('UI'):
        bs.realTimer(100, chatCmd_loop)


chatCmd_loop()


def trans(t, n, d='en'):
    try:
        t = bs.utf8(t)
        lang = translator.detect(t)
        if (lang.lang in supported_langs) or d != 'en':
            tn = bs.utf8(translator.translate(t, d).pronunciation)
            if tn is None:
                tn = bs.utf8(translator.translate(t, d).text)
            tc = bs.utf8(profanity.censor(tn))
            if tc != tn:
                import kicker
                kicker.kick(n, reason='Abuse', warn=True)
            if tc.lower() != t.lower():
                bsInternal._chatMessage(
                    t + ' ({}) ==> ({}) '.format(lang.lang, d) + tc)
    except Exception as e:
        pass


def _chatFilter(msg, clientID):
    msg = bs.uni(msg.rstrip())
    if clientID == -1:
        return msg

    if some.chatMuted and not msg == '/unmute':
        bs.screenMessage('Admin Has Muted The Chat For Some Time',
                         color=(1, 0, 0),
                         clients=[clientID],
                         transient=True)
        return None
    m = msg.split(' ')[0]
    a = msg.split(' ')[1:]
    if m in ['/pvtmsg','/dm','/pm']:
        try:
            def getPlayerFromMention(mention):
                for i in bsInternal._getForegroundHostActivity().players:
                    if i.getName().lower().find(mention.lower()) != -1:
                        return i
                else:
                    return None
            def getPlayerFromClientID(clientID):
                for i in bsInternal._getForegroundHostActivity().players:
                    if i.getInputDevice().getClientID() == clientID:
                        return i
                else:
                    return None
            if a[0].isdigit():
                for player in bsInternal._getForegroundHostActivity().players:
                    if a[0] == str(bsInternal._getForegroundHostSession().players.index(player)):
                        fr = getPlayerFromClientID(clientID)
                        what = ' '.join(a[1:]).encode('utf-8')
                        to = player
                        bs.screenMessage('Private Message Has Been Sent To {}: {}'.format(to.getName(True).encode('utf-8'),what),transient=True,clients=[fr.getInputDevice().getClientID()],color=(0,2,2))
                        bs.screenMessage('Private Message From {}: {}'.format(fr.getName(True).encode('utf-8'),what),transient=True,clients=[to.getInputDevice().getClientID()],color=(0,2,2))
            else:
                to = getPlayerFromMention(a[0])
                fr = getPlayerFromClientID(clientID)
                what = ' '.join(a[1:])
                bs.screenMessage('Private Message Has Been Sent To {}: {}'.format(to.getName(True).encode('utf-8'),what),transient=True,clients=[fr.getInputDevice().getClientID()],color=(0,2,2))
                bs.screenMessage('Private Message From {}: {}'.format(fr.getName(True).encode('utf-8'),what),transient=True,clients=[to.getInputDevice().getClientID()],color=(0,2,2))
            return None
        except Exception as e:
            bs.screenMessage('Format: /pvtmsg <name> <message>')
            print e

    if clientID in mutedIDs:
        bs.screenMessage(
            'Admin has muted you for some time. Pro Tip: Stop Begging or Spamming',
            color=(1, 0, 0),
            clients=[clientID],
            transient=True)
        return None

    r = bsInternal._getGameRoster()
    split = msg.split(' ')
    if split[0] in timeouts:
        timeout = timeouts[split[0]] * 1000
        if clientID in last:
            if (bs.getRealTime() - last[clientID][split[0]]) < timeout:
                bs.screenMessage(
                    '{} Rate-Limited. Please wait for {} seconds.'.format(
                        split[0], timeouts[split[0]] -
                        (bs.getRealTime() - last[clientID][split[0]]) / 1000),
                    color=(1, 0, 0),
                    clients=[clientID],
                    transient=True)
                return None
            else:
                last[clientID][split[0]] = bs.getRealTime()
        else:
            last[clientID] = {}
            for i in timeouts.keys():
                last[clientID][i] = -99999

    for a in r:
        if a['clientID'] == clientID:
            if len(a['players']) > 0:
                name = a['players'][0]['name']
                player = handle.getPlayerFromNick(name)
                account_id = '-' if player is None else player.get_account_id()
                playerInGame = True
            else:
                name = (a['displayString'])
                account_id = '-'
                playerInGame = False
            break
    else:
        print r
        return None
    name = bs.uni(name)

    #if not '/!' in msg: start_new_thread(db.logChat,(msg, name, account_id))  #Chat Logs

    if not db.getAdmin(account_id):
        import re
        old_msg = msg
        clean_msg = re.sub('[^A-Za-z0-9 ]+', '', msg)
        for word in filter_words:
            if re.search(r'\b({})\b'.format(word), clean_msg, re.IGNORECASE):
                cen = ''.join(
                    random.choice(list('@#$%!')) for a in range(len(word)))
                clean_msg = re.sub(r'\b({})\b'.format(word),
                                   cen,
                                   clean_msg,
                                   flags=re.IGNORECASE)
                msg = clean_msg
        if msg != old_msg:
            import kicker
            kicker.kick(name, reason='Abuse', warn=True)
            return msg

    if msg.startswith('/trans '):
        if _googletrans:
            start_new_thread(
                trans, (' '.join(msg.split(' ')[2:]), name, msg.split(' ')[1]))

    if msg.startswith('/'):
        if playerInGame:
            cmds.append([clientID, msg])
            return None if msg.startswith(
                tuple(['/kick', '/warn', '/mute', '/unmute', '/!'])) else msg
        else:
            bs.screenMessage('Please Join The Game First',
                             color=(1, 0.5, 0.5),
                             transient=True,
                             clients=[clientID])

    if 'admin' in msg.lower() or 'mod' in msg.lower(
    ) or 'promote' in msg.lower():
        for i in ['pls', 'please', 'give', 'want', 'can i']:
            if i in msg.lower():
                bs.screenMessage(
                    'Stop Begging For Admin! This Server is Self-Sufficient!',
                    color=(1, 0, 0),
                    transient=True,
                    clients=[clientID])
                import kicker
                kicker.kick(name, reason='Begging', warn=True)
                return msg

    # if not msg in some.trans:
    #   t = msg
    #  d = 'en'
    # lang = translator.detect(t)
    # if (lang.lang in supported_langs):
    #   tym = translator.translate('Translating Your Message...',lang.lang).text
    #  bs.screenMessage(tym,
    #                 color=(0, 0.5, 0.5), transient=True, clients=[clientID])
    #        tn = translator.translate(t, d).pronunciation
    #       if tn is None:
    #          tn = bs.utf8(translator.translate(t, d).text)
    #     tc = bs.utf8(profanity.censor(tn))
    #    if tc != tn:
    #       import kicker
#             kicker.kick(n, reason='Abuse', warn=True)
#        if tc.lower() != t.lower():
#           msg = '{} ({}) > {} (en)'.format(msg,lang.lang,tc)

    if not msg.lower() in some.trans and _googletrans:
        start_new_thread(trans, (msg, name))

    return msg


########INSTALL#########


def _checkInstallationForVH(autoQuit=True):
    filePath = os.path.join(os.getcwd(),
                            bs.getEnvironment().get("systemScriptsDirectory"),
                            "bsUI.py")
    if os.path.isfile(filePath):
        fileText = open(filePath).read()
        originalChatHandleText = u"def _filterChatMessage(msg, clientID):\n    return msg\n"
        replaceChatHandleText = u"def _filterChatMessage(msg, clientID):\n    try:import ChatManager;msg = ChatManager._chatFilter(msg, clientID);return(msg)\n    except:bs.printException();return(msg)\n"
        findCount = fileText.count(replaceChatHandleText)
        if findCount == 0:
            fileText = fileText.replace(originalChatHandleText,
                                        replaceChatHandleText)
            with open(filePath, "wb") as writer:
                writer.write(fileText.encode("utf-8"))
            fileText = open(filePath).read()
            if fileText.count(replaceChatHandleText) == 1:
                print("VirtualHost chat handler installed successfully!")
                with bs.Context("UI"):
                    bs.realTimer(11000, bs.Call(bs.quit))
            else:
                print("ChatManager installation failed.")
        elif findCount > 1:
            print("ChatManager was installed in a bad condition.(%d times)" %
                  findCount)
    else:
        print("ChatManager can't be installed.Cannot find bsUI.py.")


def _checkInstallationForVH2(autoQuit=True):
    filePath = os.path.join(os.getcwd(),
                            bs.getEnvironment().get("systemScriptsDirectory"),
                            "bsUI.py")
    if os.path.isfile(filePath):
        fileText = open(filePath).read()
        originalChatHandleText = u"def _handleLocalChatMessage(msg):\n    "
        replaceChatHandleText = u"def _handleLocalChatMessage(msg):\n    try:import chatCmd;chatCmd.cmd(msg)\n    except:bs.printException()\n    "
        findCount = fileText.count(replaceChatHandleText)
        if findCount == 0:
            fileText = fileText.replace(originalChatHandleText,
                                        replaceChatHandleText)
            with open(filePath, "wb") as writer:
                writer.write(fileText.encode("utf-8"))
            fileText = open(filePath).read()
            if fileText.count(replaceChatHandleText) == 1:
                print("VirtualHost chat handler installed successfully!")
                with bs.Context("UI"):
                    bs.realTimer(11000, bs.Call(bs.quit))
            else:
                print("ChatManager installation failed.")
        elif findCount > 1:
            print("ChatManager was installed in a bad condition.(%d times)" %
                  findCount)
    else:
        print("ChatManager can't be installed.Cannot find bsUI.py.")


if some.oss == 'ln':
    _checkInstallationForVH()
elif some.oss == 'nt':
    _checkInstallationForVH2()
