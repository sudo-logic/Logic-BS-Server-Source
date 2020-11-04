# -*- coding: utf-8 -*-
import json
import bs
import bsInternal
import bsPowerup
import bsUtils
import random
import some
import threading
import handle
import DB_Manager as db
import kicker
import re
import datetime
costs = {
    'nv': 10,
    'heal': 20,
    'thaw': 5,
    'sm': 100,
    'gp': 50,
    'reflections': 200
}
#costs = {'nv':10,'heal':20,'thaw':5,'sm':50,'gp':2,'reflections':20}
admincommands = [
    'except', 'cm', 'take', 'unmute', 'mute', 'maxPlayers', 'ac', 'cameraMode',
    'admin', 'kill', 'kick', 'gm', 'floater', 'curse', 'freeze', 'shatter',
    'end', 'log', 'removetag', 'remove', 'pause', 'kick', 'fly', 'ban', 'hug',
    'freeze', 'quit', 'box', 'tint', 'icy', 'lm', 'permaban', 'warn', 'unwarn',
    'rt'
]


class chatOptions(object):
    def __init__(self):
        self.all = True  # just in case
        self.tint = (0.9, 0.9, 0.9)  # needs for /nv

    def checkDevice(self, clientID, msg):
        for i in bsInternal._getForegroundHostActivity().players:
            if i.getInputDevice().getClientID() == clientID:
                player = i
                break
        else:
            return None
        n = player.get_account_id()
        if db.getAdmin(n) or msg.startswith('/!'):
            return True
        else:
            return False

    def tran(self, clientID, cost):
        cost = int(cost)
        for i in bsInternal._getForegroundHostActivity().players:
            if i.getInputDevice().getClientID() == clientID:
                n1 = i.get_account_id()
                clid = i.getInputDevice().getClientID()

        stats = db.getData(n1)

        coins = stats['p']
        if coins >= cost:
            coins -= cost
            stats['p'] = coins
            msgg = (u"This Command Cost " + str(cost) +
                    u" \ue01f. Player Now Has " + str(coins) + u' \ue01f')
            bs.screenMessage(msgg, clients=[clid], transient=True)
            db.saveData(n1, stats)
            return True
        else:
            msgg = 'The Command Costs: ' + \
                str(cost)+u'\ue01f. You Only Have: '+str(coins)+u'\ue01f'
            bs.screenMessage(msgg, clients=[clid], transient=True)
            db.saveData(n1, stats)
            return False

    def admin(self, nick):
        i = handle.getPlayerFromNick(nick)
        if i is None:
            bs.screenMessage('Error Finding Player')
            return
        n = i.get_account_id()
        print i.getName(True,False)
        try:
            db.makeAdmin(n,i.getName(True,False))
        except Exception, e: print e
        bs.screenMessage('Admin Made')

    def ban(self, nick, secs, reason):
        try:
            p = handle.getPlayerFromNick(nick)
            n = p.get_account_id()
            if n is not None:
                db.banUser(n, secs, reason)
                ac_names = handle.getAccountNamesFromAccountID(n)
                some.banned.extend(ac_names)
                for i in ac_names:
                    with bs.Context('UI'):
                        bs.realTimer(secs * 1000,
                                     bs.Call(some.banned.remove, i))
                bs.screenMessage(
                    u'{} has been banned | Reason: {} | Expires on: {}'.format(
                        p.getName(), reason,
                        (datetime.datetime.now() + datetime.timedelta(
                            seconds=secs)).strftime('%d/%m/%Y, %H:%M:%S')))
                return
            else:
                for i in bsInternal._getGameRoster():
                    #print i
                    try:
                        if bs.utf8(i['displayString']).lower().find(
                                nick.encode('utf-8').lower()) != -1 or str(
                                    i['clientID']) == nick:
                            n = handle.getAccountIDFromAccountName(
                                i['displayString'].decode('utf-8').encode(
                                    'unicode_escape'))
                            n2 = handle.getAccountNamesFromAccountID(n)
                            db.banUser(n, secs, reason)
                            bs.screenMessage(
                                u'{} has been banned | Reason: {} | Expires on: {}'
                                .format(n, reason,
                                        (datetime.datetime.now() +
                                         datetime.timedelta(seconds=secs)
                                         ).strftime('%d/%m/%Y, %H:%M:%S')))
                            some.banned.extend(n2)
                            for i in n2:
                                with bs.Context('UI'):
                                    bs.realTimer(
                                        secs * 1000,
                                        bs.Call(some.banned.remove, i))
                            return
                    except Exception as e:
                        print e
            some.permabanned = open(some.banfile).read().split('\n')
        except Exception as e:
            bs.printException()

    def kickByNick(self, nick, reason='Admin Used Kick Command'):
        kicker.kick(nick, reason)

    def opt(self, clientID, msg):
        try:
            activity = bsInternal._getForegroundHostActivity()
            with bs.Context(activity):
                checkdev = self.checkDevice(clientID, msg)
                m = msg.split(' ')[0].replace('/!', '/').replace('/', '')
                if m in admincommands and checkdev != True:
                    bs.screenMessage("You are not an admin",
                                     transient=True,
                                     clients=[clientID])
                    return
                else:
                    for i in bsInternal._getForegroundHostActivity().players:
                        if i.getInputDevice().getClientID() == clientID:
                            n = i.get_account_id()
                            player = i
                            break
                    else:
                        return
                    if m in costs and checkdev != True:
                        cost = costs[m]
                        if self.tran(clientID, cost) == False:
                            return
                    if not 'player' in locals():
                        return
                    if player is None:
                        return
                    m = msg.split(' ')[0].replace('/!', '/')  # command
                    a = msg.split(' ')[1:]  # arguments
                    if m == '/ban':
                        if len(a) < 3:
                            bs.screenMessage(
                                "Usage: /ban <name/id/clientid> <time [1m,5h,1d,etc.]> <reason>"
                            )
                        else:
                            seconds_per_unit = {
                                "s": 1,
                                "m": 60,
                                "h": 3600,
                                "d": 86400,
                                "w": 604800
                            }

                            def cts(s):
                                return int(s[:-1]) * seconds_per_unit[s[-1]]

                            self.ban(a[0], cts(a[1].lower()),
                                     (' '.join(a[2:])))
                    elif m == '/give' or m == '/donate':
                        if len(a) < 2:
                            bsInternal._chatMessage(
                                'usage: /give player_name amount')
                        else:
                            try:
                                handle.give(player, a[0], a[1],
                                            ' '.join(a[2:]))
                            except Exception as e:
                                print e.message
                    elif m == '/take':
                        if len(a) < 2:
                            bsInternal._chatMessage(
                                'usage: /take player_name amount')
                        else:
                            try:
                                handle.take(player, a[0], a[1],
                                            ' '.join(a[2:]))
                            except Exception as e:
                                print e.message
                    elif m == '/reload':
                        import autoreload
                        autoreload.update()
                        bs.reloadMedia()
                    elif m == '/redeem':
                        import json
                        codes = json.load(open(some.codefile))
                        if a[0] in codes:
                            if codes[a[0]]['s'] is None:
                                stats = db.getData(player.get_account_id())
                                stats['p'] += int(codes[a[0]]['t'])
                                db.saveData(player.get_account_id(), stats)
                                bs.screenMessage(
                                    'Congrats! You have successfully redeemed {} tickets! Join Discord for codes every 30 mins :)'
                                    .format(codes[a[0]]['t']),
                                    color=(0.5, 1, 0.5))
                                codes[a[0]]['s'] = player.getName(True)
                                open(some.codefile,
                                     'w+').write(json.dumps(codes))
                            else:
                                bs.screenMessage(
                                    u'Lol the code has already been used by {}. Sucks to be u. Join Discord for codes every 30 mins! :)'
                                    .format(codes[a[0]]['s']),
                                    color=(1, .5, .5))
                        else:
                            bs.screenMessage(
                                'No such code exists. Learn to copy stuff, dumb butt. Join Discord for codes every 30 mins :)',
                                color=(1, .5, .5))
                    elif m == '/except':
                        if len(a) >= 1:
                            if not ' '.join(a[0:]).lower() in some.trans:
                                some.trans.append((' '.join(a[0:])).lower())
                                open(some.transfile,
                                     'a').write(' '.join(a[0:]).lower() + '\n')
                                bs.screenMessage('Exception Added')
                            else:
                                bs.screenMessage(
                                    'Exception is already present')
                    elif m == '/floater':
                        playerlist = bsInternal._getForegroundHostActivity(
                        ).players
                        if not hasattr(bsInternal._getForegroundHostActivity(),
                                       'flo'):
                            import floater
                            bsInternal._getForegroundHostActivity().flo = floater.Floater(bsInternal._getForegroundHostActivity()._mapType())
                        floater = bsInternal._getForegroundHostActivity().flo
                        if floater.controlled:
                            bs.screenMessage(
                                'Floater is already being controlled',
                                color=(1, 0, 0))
                            return
                        for i in playerlist:
                            if i.getInputDevice().getClientID() == clientID:
                                clientID = i.getInputDevice().getClientID()
                                bs.screenMessage(
                                    'You\'ve Gained Control Over The Floater!\nPress Bomb to Throw Bombs and Punch to leave!\nYou will automatically get released after some time!',
                                    clients=[clientID],
                                    transient=True,
                                    color=(0, 1, 1))

                                def dis(i, floater):
                                    i.actor.node.invincible = False
                                    i.resetInput()
                                    i.actor.connectControlsToPlayer()
                                    floater.dis()

                                # bs.gameTimer(15000,bs.Call(dis,i,floater))
                                ps = i.actor.node.position
                                i.actor.node.invincible = True
                                floater.node.position = (ps[0], ps[1] + 1.5,
                                                         ps[2])
                                i.actor.node.holdNode = bs.Node(None)
                                i.actor.node.holdNode = floater.node2
                                i.actor.disconnectControlsFromPlayer()
                                i.resetInput()
                                floater.sourcePlayer = i
                                floater.con()
                                i.assignInputCall('pickUpPress', floater.up)
                                i.assignInputCall('pickUpRelease', floater.upR)
                                i.assignInputCall('jumpPress', floater.down)
                                i.assignInputCall('jumpRelease', floater.downR)
                                i.assignInputCall('bombPress', floater.drop)
                                i.assignInputCall('punchPress',
                                                  bs.Call(dis, i, floater))
                                i.assignInputCall('upDown', floater.updown)
                                i.assignInputCall('leftRight',
                                                  floater.leftright)
                                i.actor.afk_checker = None

                    elif m == '/mute':
                        if a == []:
                            bsInternal._chatMessage('Admin Muted The Chat')

                            def unmute():
                                if some.chatMuted:
                                    some.chatMuted = False
                                    bs.screenMessage('ChatMute Timed-Out',
                                                     transient=True,
                                                     color=(0.5, 0.5, 1))

                            with bs.Context('UI'):
                                bs.realTimer(120000, unmute)
                            some.chatMuted = True
                        else:
                            kicker.kick(a[0],
                                        reason=' '.join(a[1:]),
                                        mute=True,
                                        warn=True)
                    elif m == '/unmute':
                        bsInternal._chatMessage('Admin UnMuted The Chat')
                        some.chatMuted = False
                        import ChatManager
                        ChatManager.mutedIDs = []
                    elif m == '/contact':
                        bsInternal._chatMessage(
                            'Join RAGE For Regular Server Updates!')
                        bsInternal._chatMessage(
                            'Link https://bit.ly/awesomelogic')
                        bsInternal._chatMessage('Discord: AwesomeLogic#2236')
                        bsInternal._chatMessage('Telegram: @AwesomeLogic')
                        bs.screenMessage('\n' * 1000)
                    elif m == '/log':
                        open(some.logfile,
                             'a+').write('\n' * 5 +
                                         str(bsInternal._getGameRoster()) +
                                         '\n' +
                                         str(bsInternal._getChatMessages()))
                    elif m == '/whois':
                        if a == []:
                            bs.screenMessage('No Rank Provided')
                        elif not a[0].isdigit():
                            bs.screenMessage('Not A Valid Rank')
                        else:
                            handle.me(db.getUserFromRank(int(a[0])))
                    elif m == '/ip':
                        import reboot
                        bsInternal._chatMessage('IP: {} | Port: {}'.format(
                            reboot.ip, reboot.port))
                    elif m == '/me' or m == '/stats' or m == '/rank' or m == '/myself' or m == '/ranks':
                        if a == []:
                            handle.me(player)
                        else:
                            handle.me(handle.getPlayerFromNick(a[0]))
                    elif m in ['/inv', '/inventory', '/items']:
                        if a == []:
                            handle.inv(player)
                        else:
                            handle.inv(handle.getPlayerFromNick(a[0]))
                    elif m == '/shop':
                        bsInternal._chatMessage("You can buy these:")
                        bsInternal._chatMessage(
                            "Use /buy <name_of_perk> <no_of_days>")

                        bsInternal._chatMessage('==========COMMANDS=========')
                        for i, k in costs.items():
                            bsInternal._chatMessage(
                                u"Command: /{} {} Cost: {} \ue01f".format(
                                    i, ' ' * (20 - len(i)), str(k)))

                        bsInternal._chatMessage('==========PERKS=========')
                        for i, k in some.prices.items():
                            bsInternal._chatMessage(
                                u"Name: {} {} Details: {} {} Cost: {} \ue01f/Day"
                                .format(i.capitalize(), (' ' * (20 - len(i))),
                                        k['d'], (' ' * (20 - len(i))),
                                        str(k['c'])))

                        bs.screenMessage('\n' * 1000)
                    elif m == '/removetag':
                        n = handle.getPlayerFromNick(a[0]).get_account_id()
                        stats = db.getData(n)
                        stats['t'] = ''
                        bs.screenMessage('Tag Removed')
                        db.saveData(n, stats)

                    elif m == '/throw':
                        if a == []:
                            bs.screenMessage('No Item Specified')
                        else:
                            item = a[0]
                            import json
                            for i in bsInternal._getForegroundHostActivity(
                            ).players:
                                if i.getInputDevice().getClientID(
                                ) == clientID:
                                    n = i.get_account_id()
                                    break
                            else:
                                return
                            if True:
                                try:
                                    stats = db.getData(n)
                                    if item in stats['i']:
                                        stats['i'].pop(item)
                                        bs.screenMessage('Item Thrown Away')
                                    db.saveData(n, stats)
                                except Exception as e:
                                    print e
                                    return
                    elif m == '/id':
                        i = player
                        if i is not None:
                            n = i.get_account_id()
                            n2 = i.getInputDevice().getClientID()
                            bsInternal._chatMessage(
                                'Unique ID For Player %s : %s' %
                                (i.getName(True), n))
                        else:
                            #bs.screenMessage("Join Game First")
                            return
                    elif m == '/convert':
                        if len(a) == 1:
                            handle.convert(player, a[0])
                        else:
                            bsInternal._chatMessage('Usage: /convert amount')
                    elif m == '/bet' or m == '/gamble':
                        if a == []:
                            bs.screenMessage(
                                'You also need to enter the amount. Fool.',
                                color=(1, .5, .5))
                            bsInternal._chatMessage(
                                'Usage: /bet [amount/all/half]')
                        else:
                            handle.bet(player, a[0])
                    elif m == '/beg':
                        handle.beg(player)
                    elif m == '/daily':
                        try:
                            handle.daily(clientID)
                        except Exception as e:
                            print e
                    elif m == '/buy':
                        if a == []:
                            bsInternal._chatMessage(
                                'Item name not provided. Use /shop to get a list.'
                            )
                        else:
                            a[0] = bs.utf8(a[0]).lower()
                            if a[0] in some.prices:
                                import json
                                for i in bsInternal._getForegroundHostActivity(
                                ).players:
                                    if i.getInputDevice().getClientID(
                                    ) == clientID:
                                        n = i.get_account_id()
                                        break
                                else:
                                    return
                                if True:
                                    try:
                                        stats = {}
                                        stats = db.getData(n)
                                    except Exception as e:
                                        print e, '/buy get error'
                                        return
                                if a[0] in stats['i'] and a[0] not in ['tag']:
                                    bs.screenMessage(
                                        'You Already Have This Item!')
                                    return
                                if ('backflip' in stats['i'] and a[0] == 'backflip-protection') or 'backflip-protection' in stats['i'] and a[0] == 'backflip':
                                    bs.screenMessage(
                                        'You can\'t have both backflip and backflip-protection!')
                                    return
                                if a[0] != 'tag':
                                    try:
                                        limitDay = int(a[1])
                                        a[1] = int(a[1])
                                    except:
                                        limitDay = 1
                                else:
                                    limitDay = 9999
                                try:
                                    if stats['p'] >= (some.prices[a[0]]['c'] *
                                                      limitDay):
                                        stats['p'] -= (some.prices[a[0]]['c'] *
                                                       limitDay)
                                        import datetime
                                        expire_time = long(
                                            (datetime.datetime.now() +
                                             datetime.timedelta(days=limitDay)
                                             ).strftime("%Y%m%d%H%M")
                                        )  # (str(7*(len(History)//3)),"%d")
                                        if a[0] == 'tag':
                                            tag = ' '.join(a[1:])
                                            if len(tag) > 20:
                                                return
                                            tag = bs.uni(tag).replace(
                                                '/c', u'\ue043').replace(
                                                    '/d', u'\ue048')
                                            if not any(i in re.sub(
                                                    '[^A-Za-z0-9]+', '',
                                                    tag.lower()) for i in [
                                                        'moderator', 'admin',
                                                        'owner'
                                                    ]) and not tag.startswith(
                                                        u'\ue048#'):
                                                stats['t'] = tag
                                            else:
                                                return
                                        stats['i'].update({a[0]: expire_time})
                                        bs.screenMessage(
                                            'Purchase Successful! Expires on: {} | Use /throw {} to remove it'
                                            .format(
                                                (datetime.datetime.strptime(
                                                    str(expire_time),
                                                    "%Y%m%d%H%M").strftime(
                                                        "%d-%m-%Y %H:%M:%S")),
                                                a[0]))
                                        db.saveData(n, stats)
                                    else:
                                        bs.screenMessage(u'Not Enough \ue01f')
                                except Exception as e:
                                    print e
                            else:
                                bs.screenMessage("No Such Item Exists!")
                    if m == '/unban':
                        some.banned = []
                    if m == '/kick':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /kick name or number of list')
                        else:
                            reason = ' '.join(
                                a[1:]) if ' '.join(a[1:]) != '' else None
                            self.kickByNick(a[0], reason=reason)
                    if m == '/unwarn':
                        some.warn = {}
                        bs.screenMessage('All warns have been reset')
                    if m == '/warn':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /warn name or number of list')
                        else:
                            reason = ' '.join(
                                a[1:]) if ' '.join(a[1:]) != '' else None
                            kicker.kick(a[0], reason=reason, warn=True)
                    elif m == '/list':
                        bsInternal._chatMessage(
                            "======== FOR /kick ONLY: ========")
                        for i in bsInternal._getGameRoster():
                            try:
                                bsInternal._chatMessage(
                                    i['players'][0]['nameFull'] +
                                    "     (/kick " + str(i['clientID']) + ")")
                            except:
                                bsInternal._chatMessage(i['displayString'] +
                                                        "     (/kick " +
                                                        str(i['clientID']) +
                                                        ")")
                        bsInternal._chatMessage(
                            "==================================")
                        bsInternal._chatMessage(
                            "======= For other commands: =======")
                        for s in bsInternal._getForegroundHostSession(
                        ).players:
                            bsInternal._chatMessage(
                                s.getName() + "     " +
                                str(bsInternal._getForegroundHostSession().
                                    players.index(s)))
                        bs.screenMessage('\n' * 1000)
                    elif m == '/ooh':
                        if a is not None and len(a) > 0:
                            s = int(a[0])

                            def oohRecurce(c):
                                bs.playSound(bs.getSound('ooh'), volume=2)
                                c -= 1
                                if c > 0:
                                    bs.gameTimer(
                                        int(a[1]) if len(a) > 1
                                        and a[1] is not None else 1000,
                                        bs.Call(oohRecurce, c=c))

                            oohRecurce(c=s)
                        else:
                            bs.playSound(bs.getSound('ooh'), volume=2)
                    elif m == '/playSound':
                        if a is not None and len(a) > 1:
                            s = int(a[1])

                            def oohRecurce(c):
                                bs.playSound(bs.getSound(str(a[0])), volume=2)
                                c -= 1
                                if c > 0:
                                    bs.gameTimer(
                                        int(a[2]) if len(a) > 2
                                        and a[2] is not None else 1000,
                                        bs.Call(oohRecurce, c=c))

                            oohRecurce(c=s)
                        else:
                            bs.playSound(bs.getSound(str(a[0])), volume=2)
                    elif m == '/quit':
                        bsInternal.quit()
                    elif m == '/nv':
                        if self.tint is None:
                            self.tint = bs.getSharedObject('globals').tint
                        bs.getSharedObject('globals').tint = (
                            0.5, 0.7,
                            1) if a == [] or not a[0] == u'off' else self.tint
                    elif m == '/admin':
                        s = a[0]
                        self.admin(s)
                    elif m == '/permaban':
                        s = str(a[0])
                        self.permaban(s)
                    elif m == '/freeze':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /freeze all or number of list')
                        else:
                            if a[0] == 'all':
                                for i in bs.getSession().players:
                                    try:
                                        i.actor.node.handleMessage(
                                            bs.FreezeMessage())
                                    except:
                                        pass
                            else:
                                bs.getSession().players[int(
                                    a[0])].actor.node.handleMessage(
                                        bs.FreezeMessage())
                    elif m == '/thaw':
                        if a == []:
                            for i in range(len(activity.players)):
                                if activity.players[i].getInputDevice(
                                ).getClientID() == clientID:
                                    bsInternal._getForegroundHostActivity(
                                    ).players[i].actor.node.handleMessage(
                                        bs.ThawMessage())
                        else:
                            if a[0] == 'all':
                                for i in bs.getSession().players:
                                    try:
                                        i.actor.node.handleMessage(
                                            bs.ThawMessage())
                                    except:
                                        pass
                            else:
                                bs.getSession().players[int(
                                    a[0])].actor.node.handleMessage(
                                        bs.ThawMessage())
                    elif m == '/kill':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /kill all or number of list')
                        else:
                            if a[0] == 'all':
                                for i in bs.getSession().players:
                                    try:
                                        i.actor.node.handleMessage(
                                            bs.DieMessage())
                                    except:
                                        pass
                            else:
                                bs.getSession().players[int(
                                    a[0])].actor.node.handleMessage(
                                        bs.DieMessage())
                    elif m == '/curse':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /curse all or number of list')
                        else:
                            if a[0] == 'all':
                                for i in bs.getSession().players:
                                    try:
                                        i.actor.curse()
                                    except:
                                        pass
                            else:
                                bs.getSession().players[int(
                                    a[0])].actor.curse()
                    elif m == '/box':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /box all or number of list')
                        else:
                            try:
                                if a[0] == 'all':
                                    for i in bs.getSession().players:
                                        try:
                                            i.actor.node.torsoModel = bs.getModel(
                                                "tnt")
                                        except:
                                            pass
                                    for i in bs.getSession().players:
                                        try:
                                            i.actor.node.colorMaskTexture = bs.getTexture(
                                                "tnt")
                                        except:
                                            pass
                                    for i in bs.getSession().players:
                                        try:
                                            i.actor.node.colorTexture = bs.getTexture(
                                                "tnt")
                                        except:
                                            pass
                                    for i in bs.getSession().players:
                                        try:
                                            i.actor.node.highlight = (1, 1, 1)
                                        except:
                                            pass
                                    for i in bs.getSession().players:
                                        try:
                                            i.actor.node.color = (1, 1, 1)
                                        except:
                                            pass
                                    for i in bs.getSession().players:
                                        try:
                                            i.actor.node.headModel = None
                                        except:
                                            pass
                                    for i in bs.getSession().players:
                                        try:
                                            i.actor.node.style = "cyborg"
                                        except:
                                            pass
                                else:
                                    n = int(a[0])
                                    bs.getSession().players[
                                        n].actor.node.torsoModel = bs.getModel(
                                            "tnt")
                                    bs.getSession().players[
                                        n].actor.node.colorMaskTexture = bs.getTexture(
                                            "tnt")
                                    bs.getSession().players[
                                        n].actor.node.colorTexture = bs.getTexture(
                                            "tnt")
                                    bs.getSession(
                                    ).players[n].actor.node.highlight = (1, 1,
                                                                         1)
                                    bs.getSession(
                                    ).players[n].actor.node.color = (1, 1, 1)
                                    bs.getSession(
                                    ).players[n].actor.node.headModel = None
                                    bs.getSession(
                                    ).players[n].actor.node.style = "cyborg"
                            except:
                                bs.screenMessage('Error!', color=(1, 0, 0))
                    elif m == '/remove':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /remove all or number of list')
                        else:
                            if a[0] == 'all':
                                for i in bs.getSession().players:
                                    try:
                                        i.removeFromGame()
                                    except:
                                        pass
                            else:
                                bs.getSession().players[int(
                                    a[0])].removeFromGame()
                    elif m == '/end':
                        try:
                            bsInternal._getForegroundHostActivity().endGame()
                        except:
                            pass
                    elif m == '/hug':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /hug all or number of list')
                        else:
                            try:
                                if a[0] == 'all':
                                    try:
                                        bsInternal._getForegroundHostActivity(
                                        ).players[
                                            0].actor.node.holdNode = bsInternal._getForegroundHostActivity(
                                            ).players[1].actor.node
                                    except:
                                        pass
                                    try:
                                        bsInternal._getForegroundHostActivity(
                                        ).players[
                                            1].actor.node.holdNode = bsInternal._getForegroundHostActivity(
                                            ).players[0].actor.node
                                    except:
                                        pass
                                    try:
                                        bsInternal._getForegroundHostActivity(
                                        ).players[
                                            3].actor.node.holdNode = bsInternal._getForegroundHostActivity(
                                            ).players[2].actor.node
                                    except:
                                        pass
                                    try:
                                        bsInternal._getForegroundHostActivity(
                                        ).players[
                                            4].actor.node.holdNode = bsInternal._getForegroundHostActivity(
                                            ).players[3].actor.node
                                    except:
                                        pass
                                    try:
                                        bsInternal._getForegroundHostActivity(
                                        ).players[
                                            5].actor.node.holdNode = bsInternal._getForegroundHostActivity(
                                            ).players[6].actor.node
                                    except:
                                        pass
                                    try:
                                        bsInternal._getForegroundHostActivity(
                                        ).players[
                                            6].actor.node.holdNode = bsInternal._getForegroundHostActivity(
                                            ).players[7].actor.node
                                    except:
                                        pass
                                else:
                                    bsInternal._getForegroundHostActivity(
                                    ).players[int(
                                        a[0]
                                    )].actor.node.holdNode = bsInternal._getForegroundHostActivity(
                                    ).players[int(a[1])].actor.node
                            except:
                                bs.screenMessage('Error!', color=(1, 0, 0))
                    elif m == '/gm':
                        if a == []:
                            for i in range(len(activity.players)):
                                if activity.players[i].getInputDevice(
                                ).getClientID() == clientID:
                                    activity.players[
                                        i].actor.node.hockey = activity.players[
                                            i].actor.node.hockey == False
                                    activity.players[
                                        i].actor.node.invincible = activity.players[
                                            i].actor.node.invincible == False
                                    activity.players[
                                        i].actor._punchPowerScale = 5 if activity.players[
                                            i].actor._punchPowerScale == 1.2 else 1.2
                        else:
                            activity.players[int(
                                a[0])].actor.node.hockey = activity.players[
                                    int(a[0])].actor.node.hockey == False
                            activity.players[int(
                                a[0]
                            )].actor.node.invincible = activity.players[int(
                                a[0])].actor.node.invincible == False
                            activity.players[int(
                                a[0]
                            )].actor._punchPowerScale = 5 if activity.players[
                                int(a[0]
                                    )].actor._punchPowerScale == 1.2 else 1.2
                    elif m == '/tint':
                        if a == []:
                            bsInternal._chatMessage('Using: /tint R G B')
                            bsInternal._chatMessage('OR')
                            bsInternal._chatMessage(
                                'Using: /tint r bright speed')
                        else:
                            if a[0] == 'r':
                                m = 1.3 if a[1] is None else float(a[1])
                                s = 1000 if a[2] is None else float(a[2])
                                bsUtils.animateArray(
                                    bs.getSharedObject('globals'), 'tint', 3, {
                                        0: (1 * m, 0, 0),
                                        s: (0, 1 * m, 0),
                                        s * 2: (0, 0, 1 * m),
                                        s * 3: (1 * m, 0, 0)
                                    }, True)
                            else:
                                try:
                                    if a[1] is not None:
                                        bs.getSharedObject('globals').tint = (
                                            float(a[0]), float(a[1]),
                                            float(a[2]))
                                    else:
                                        bs.screenMessage('Error!',
                                                         color=(1, 0, 0))
                                except:
                                    bs.screenMessage('Error!', color=(1, 0, 0))
                    elif m == '/pause':
                        bs.getSharedObject(
                            'globals').paused = bs.getSharedObject(
                                'globals').paused == False
                    elif m == '/sm':
                        bs.getSharedObject(
                            'globals').slowMotion = bs.getSharedObject(
                                'globals').slowMotion == False
                    # elif m == '/bunny':
                    #     if a == []:
                    #         bsInternal._chatMessage('Using: /bunny count owner(number of list)')
                    #     import BuddyBunny
                    #     for i in range(int(a[0])):
                    #         p=bs.getSession().players[int(a[1])]
                    #         if not 'bunnies' in p.gameData:
                    #             p.gameData['bunnies'] = BuddyBunny.BunnyBotSet(p)
                    #         p.gameData['bunnies'].doBunny()
                    elif m == '/cameraMode':
                        try:
                            if bs.getSharedObject(
                                    'globals').cameraMode == 'follow':
                                bs.getSharedObject(
                                    'globals').cameraMode = 'rotate'
                            else:
                                bs.getSharedObject(
                                    'globals').cameraMode = 'follow'
                        except:
                            pass
                    elif m == '/lm':
                        arr = []
                        for i in range(100):
                            try:
                                arr.append(bsInternal._getChatMessages()[-1 -
                                                                         i])
                            except:
                                pass
                        arr.reverse()
                        for i in arr:
                            if not 'Server67323: ' in i:
                                bsInternal._chatMessage(i)
                    elif m == '/gp':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /gp number of list')
                        else:
                            s = bsInternal._getForegroundHostSession()
                            for i in s.players[int(a[0])].getInputDevice(
                            )._getPlayerProfiles():
                                try:
                                    bsInternal._chatMessage(i)
                                except:
                                    pass
                            bs.screenMessage('\n' * 1000)
                    elif m == '/joke':
                        threading.Thread(target=handle.joke,
                                         args=(player.getName(
                                             True, False), )).start()

                    elif m == '/icy':
                        bsInternal._getForegroundHostActivity().players[int(
                            a[0]
                        )].actor.node = bsInternal._getForegroundHostActivity(
                        ).players[int(a[1])].actor.node
                    elif m == '/fly':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /fly all or number of list')
                        else:
                            if a[0] == 'all':
                                for i in bsInternal._getForegroundHostActivity(
                                ).players:
                                    i.actor.node.fly = True
                            else:
                                bsInternal._getForegroundHostActivity(
                                ).players[int(
                                    a[0]
                                )].actor.node.fly = bsInternal._getForegroundHostActivity(
                                ).players[int(a[0])].actor.node.fly == False
                    elif m == '/floorReflection':
                        bs.getSharedObject(
                            'globals').floorReflection = bs.getSharedObject(
                                'globals').floorReflection == False
                    elif m == '/ac':
                        if a == []:
                            bsInternal._chatMessage('Using: /ac R G B')
                            bsInternal._chatMessage('OR')
                            bsInternal._chatMessage(
                                'Using: /ac r bright speed')
                        else:
                            if a[0] == 'r':
                                m = 1.3 if a[1] is None else float(a[1])
                                s = 1000 if a[2] is None else float(a[2])
                                bsUtils.animateArray(
                                    bs.getSharedObject('globals'),
                                    'ambientColor', 3, {
                                        0: (1 * m, 0, 0),
                                        s: (0, 1 * m, 0),
                                        s * 2: (0, 0, 1 * m),
                                        s * 3: (1 * m, 0, 0)
                                    }, True)
                            else:
                                try:
                                    if a[1] is not None:
                                        bs.getSharedObject(
                                            'globals').ambientColor = (float(
                                                a[0]), float(a[1]), float(
                                                    a[2]))
                                    else:
                                        bs.screenMessage('Error!',
                                                         color=(1, 0, 0))
                                except:
                                    bs.screenMessage('Error!', color=(1, 0, 0))
                    elif m == '/rt':
                        global times
                        if a == []:
                            choice = 1
                        else:
                            choice = int(a[0])
                        times = 1
                        defdict = {}

                        def fix():
                            for i, k in defdict.items():
                                try:
                                    i.colorTexture = k
                                except:
                                    pass

                        def asset():
                            global times
                            nodes = bs.getNodes()
                            times += 1
                            assets = []
                            models = []
                            assetnames = [
                                'achievementBoxer', 'achievementCrossHair',
                                'achievementDualWielding', 'achievementEmpty',
                                'achievementFlawlessVictory',
                                'achievementFootballShutout',
                                'achievementFootballVictory',
                                'achievementFreeLoader',
                                'achievementGotTheMoves',
                                'achievementInControl',
                                'achievementMedalLarge',
                                'achievementMedalMedium',
                                'achievementMedalSmall', 'achievementMine',
                                'achievementOffYouGo', 'achievementOnslaught',
                                'achievementOutline', 'achievementRunaround',
                                'achievementSharingIsCaring',
                                'achievementStayinAlive',
                                'achievementSuperPunch', 'achievementTNT',
                                'achievementTeamPlayer', 'achievementWall',
                                'achievementsIcon', 'actionButtons',
                                'actionHeroColor', 'actionHeroColorMask',
                                'actionHeroIcon', 'actionHeroIconColorMask',
                                'advancedIcon', 'agentColor', 'agentColorMask',
                                'agentIcon', 'agentIconColorMask',
                                'aliBSRemoteIOSQR', 'aliColor', 'aliColorMask',
                                'aliControllerQR', 'aliIcon',
                                'aliIconColorMask', 'aliSplash', 'alienColor',
                                'alienColorMask', 'alienIcon',
                                'alienIconColorMask', 'alwaysLandBGColor',
                                'alwaysLandLevelColor', 'alwaysLandPreview',
                                'analogStick', 'arrow', 'assassinColor',
                                'assassinColorMask', 'assassinIcon',
                                'assassinIconColorMask', 'audioIcon',
                                'backIcon', 'bar', 'bearColor',
                                'bearColorMask', 'bearIcon',
                                'bearIconColorMask', 'bg', 'bigG',
                                'bigGPreview', 'black', 'bombButton',
                                'bombColor', 'bombColorIce', 'bombStickyColor',
                                'bonesColor', 'bonesColorMask', 'bonesIcon',
                                'bonesIconColorMask', 'boxingGlovesColor',
                                'bridgitLevelColor', 'bridgitPreview',
                                'bunnyColor', 'bunnyColorMask', 'bunnyIcon',
                                'bunnyIconColorMask', 'buttonBomb',
                                'buttonJump', 'buttonPickUp', 'buttonPunch',
                                'buttonSquare', 'chTitleChar1', 'chTitleChar2',
                                'chTitleChar3', 'chTitleChar4', 'chTitleChar5',
                                'characterIconMask', 'chestIcon',
                                'chestIconEmpty', 'chestIconMulti',
                                'chestOpenIcon', 'circle', 'circleNoAlpha',
                                'circleOutline', 'circleOutlineNoAlpha',
                                'circleShadow', 'circleZigZag', 'coin',
                                'controllerIcon', 'courtyardLevelColor',
                                'courtyardPreview', 'cowboyColor',
                                'cowboyColorMask', 'cowboyIcon',
                                'cowboyIconColorMask', 'cragCastleLevelColor',
                                'cragCastlePreview', 'crossOut',
                                'crossOutMask', 'cursor', 'cuteSpaz',
                                'cyborgColor', 'cyborgColorMask', 'cyborgIcon',
                                'cyborgIconColorMask', 'doomShroomBGColor',
                                'doomShroomLevelColor', 'doomShroomPreview',
                                'downButton', 'egg1', 'egg2', 'egg3', 'egg4',
                                'eggTex1', 'eggTex2', 'eggTex3', 'empty',
                                'explosion', 'eyeColor', 'eyeColorTintMask',
                                'file', 'flagColor', 'flagPoleColor', 'folder',
                                'fontBig', 'fontExtras', 'fontExtras2',
                                'fontExtras3', 'fontExtras4', 'fontSmall0',
                                'fontSmall1', 'fontSmall2', 'fontSmall3',
                                'fontSmall4', 'fontSmall5', 'fontSmall6',
                                'fontSmall7', 'footballStadium',
                                'footballStadiumPreview', 'frameInset',
                                'frostyColor', 'frostyColorMask', 'frostyIcon',
                                'frostyIconColorMask', 'fuse',
                                'gameCenterIcon', 'gameCircleIcon',
                                'gladiatorColor', 'gladiatorColorMask',
                                'gladiatorIcon', 'gladiatorIconColorMask',
                                'glow', 'googlePlayAchievementsIcon',
                                'googlePlayGamesIcon',
                                'googlePlayLeaderboardsIcon', 'googlePlusIcon',
                                'googlePlusSignInButton', 'graphicsIcon',
                                'heart', 'hockeyStadium',
                                'hockeyStadiumPreview', 'iconOnslaught',
                                'iconRunaround', 'impactBombColor',
                                'impactBombColorLit', 'inventoryIcon',
                                'jackColor', 'jackColorMask', 'jackIcon',
                                'jackIconColorMask', 'jumpsuitColor',
                                'jumpsuitColorMask', 'jumpsuitIcon',
                                'jumpsuitIconColorMask', 'kronk',
                                'kronkColorMask', 'kronkIcon',
                                'kronkIconColorMask', 'lakeFrigid',
                                'lakeFrigidPreview', 'lakeFrigidReflections',
                                'landMine', 'landMineLit', 'leaderboardsIcon',
                                'leftButton', 'levelIcon', 'light',
                                'lightSharp', 'lightSoft', 'lock', 'logIcon',
                                'logo', 'logoEaster', 'mapPreviewMask',
                                'medalBronze', 'medalComplete', 'medalGold',
                                'medalSilver', 'melColor', 'melColorMask',
                                'melIcon', 'melIconColorMask', 'menuBG',
                                'menuButton', 'menuIcon', 'meter',
                                'monkeyFaceLevelColor', 'monkeyFacePreview',
                                'multiplayerExamples', 'natureBackgroundColor',
                                'neoSpazColor', 'neoSpazColorMask',
                                'neoSpazIcon', 'neoSpazIconColorMask',
                                'nextLevelIcon', 'ninjaColor',
                                'ninjaColorMask', 'ninjaIcon',
                                'ninjaIconColorMask', 'nub', 'null',
                                'oldLadyColor', 'oldLadyColorMask',
                                'oldLadyIcon', 'oldLadyIconColorMask',
                                'operaSingerColor', 'operaSingerColorMask',
                                'operaSingerIcon', 'operaSingerIconColorMask',
                                'ouyaAButton', 'ouyaIcon', 'ouyaOButton',
                                'ouyaUButton', 'ouyaYButton', 'penguinColor',
                                'penguinColorMask', 'penguinIcon',
                                'penguinIconColorMask', 'pixieColor',
                                'pixieColorMask', 'pixieIcon',
                                'pixieIconColorMask', 'playerLineup',
                                'powerupBomb', 'powerupCurse', 'powerupHealth',
                                'powerupIceBombs', 'powerupImpactBombs',
                                'powerupLandMines', 'powerupPunch',
                                'powerupShield', 'powerupSpeed',
                                'powerupStickyBombs', 'puckColor',
                                'rampageBGColor', 'rampageBGColor2',
                                'rampageLevelColor', 'rampagePreview',
                                'reflectionChar_+x', 'reflectionChar_+y',
                                'reflectionChar_+z', 'reflectionChar_-x',
                                'reflectionChar_-y', 'reflectionChar_-z',
                                'reflectionPowerup_+x', 'reflectionPowerup_+y',
                                'reflectionPowerup_+z', 'reflectionPowerup_-x',
                                'reflectionPowerup_-y', 'reflectionPowerup_-z',
                                'reflectionSharp_+x', 'reflectionSharp_+y',
                                'reflectionSharp_+z', 'reflectionSharp_-x',
                                'reflectionSharp_-y', 'reflectionSharp_-z',
                                'reflectionSharper_+x', 'reflectionSharper_+y',
                                'reflectionSharper_+z', 'reflectionSharper_-x',
                                'reflectionSharper_-y', 'reflectionSharper_-z',
                                'reflectionSharpest_+x',
                                'reflectionSharpest_+y',
                                'reflectionSharpest_+z',
                                'reflectionSharpest_-x',
                                'reflectionSharpest_-y',
                                'reflectionSharpest_-z', 'reflectionSoft_+x',
                                'reflectionSoft_+y', 'reflectionSoft_+z',
                                'reflectionSoft_-x', 'reflectionSoft_-y',
                                'reflectionSoft_-z', 'replayIcon',
                                'rgbStripes', 'rightButton', 'robotColor',
                                'robotColorMask', 'robotIcon',
                                'robotIconColorMask', 'roundaboutLevelColor',
                                'roundaboutPreview', 'santaColor',
                                'santaColorMask', 'santaIcon',
                                'santaIconColorMask', 'scorch', 'scorchBig',
                                'scrollWidget', 'scrollWidgetGlow',
                                'settingsIcon', 'shadow', 'shadowSharp',
                                'shadowSoft', 'shield', 'shrapnel1Color',
                                'slash', 'smoke', 'softRect', 'softRect2',
                                'softRectVertical', 'sparks', 'star',
                                'startButton', 'stepRightUpLevelColor',
                                'stepRightUpPreview', 'storeCharacter',
                                'storeCharacterEaster', 'storeCharacterXmas',
                                'storeIcon', 'superheroColor',
                                'superheroColorMask', 'superheroIcon',
                                'superheroIconColorMask', 'textClearButton',
                                'thePadLevelColor', 'thePadPreview',
                                'ticketRoll', 'ticketRollBig', 'ticketRolls',
                                'tickets', 'ticketsMore', 'tipTopBGColor',
                                'tipTopLevelColor', 'tipTopPreview', 'tnt',
                                'touchArrows', 'touchArrowsActions',
                                'towerDLevelColor', 'towerDPreview',
                                'treesColor', 'trophy', 'tv', 'uiAtlas',
                                'uiAtlas2', 'upButton', 'usersButton',
                                'vrFillMound', 'warriorColor',
                                'warriorColorMask', 'warriorIcon',
                                'warriorIconColorMask', 'white',
                                'windowHSmallVMed', 'windowHSmallVSmall',
                                'wings', 'witchColor', 'witchColorMask',
                                'witchIcon', 'witchIconColorMask',
                                'wizardColor', 'wizardColorMask', 'wizardIcon',
                                'wizardIconColorMask', 'wrestlerColor',
                                'wrestlerColorMask', 'wrestlerIcon',
                                'wrestlerIconColorMask', 'zigZagLevelColor',
                                'zigzagPreview', 'zoeColor', 'zoeColorMask',
                                'zoeIcon', 'zoeIconColorMask'
                            ]
                            for i in assetnames:
                                assets.append(bs.getTexture(i))
                            # for i in nodes:
                            # if hasattr(i,'colorTexture'):
                            #if i.colorTexture not in assets:assets.append(i.colorTexture)
                            # if hasattr(i,'model'):
                            #   if i.model not in models:models.append(i.model)
                            for i in nodes:
                                if hasattr(i, 'colorTexture'):
                                    if i not in defdict:
                                        defdict.update({i: i.colorTexture})
                                    i.colorTexture = random.choice(assets)
                                # if hasattr(i,'model'):
                                #   i.model = random.choice(models)
                            if times <= choice:
                                bs.gameTimer(1000, asset)
                            else:
                                bs.gameTimer(1000, fix)

                        asset()
                    elif m == '/iceOff':
                        try:
                            activity.getMap().node.materials = [
                                bs.getSharedObject('footingMaterial')
                            ]
                            activity.getMap().isHockey = False
                        except:
                            pass
                        try:
                            activity.getMap().floor.materials = [
                                bs.getSharedObject('footingMaterial')
                            ]
                            activity.getMap().isHockey = False
                        except:
                            pass
                        for i in activity.players:
                            i.actor.node.hockey = False
                    elif m == '/maxPlayers':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /maxPlayers count of players')
                        else:
                            try:
                                #bsInternal._getForegroundHostSession()._maxPlayers = int(a[0])
                                import detect
                                detect.maxPlayers = int(a[0])
                                bsInternal._setPublicPartyMaxSize(int(a[0]))
                                bsInternal._chatMessage(
                                    'Players limit set to ' + str(int(a[0])))
                            except:
                                bs.screenMessage('Error!', color=(1, 0, 0))
                    elif m == '/heal':
                        if a == []:
                            for i in range(len(activity.players)):
                                if activity.players[i].getInputDevice(
                                ).getClientID() == clientID:
                                    bsInternal._getForegroundHostActivity(
                                    ).players[i].actor.node.handleMessage(
                                        bs.PowerupMessage(
                                            powerupType='health'))
                        else:
                            try:
                                bsInternal._getForegroundHostActivity(
                                ).players[int(a[0])].actor.node.handleMessage(
                                    bs.PowerupMessage(powerupType='health'))
                            except:
                                bs.screenMessage('Error!', color=(1, 0, 0))
                    elif m == '/reflections':
                        if a == [] or len(a) < 2:
                            bsInternal._chatMessage(
                                'Using: /reflections type(1/0) scale')
                        else:
                            rs = [int(a[1])]
                            type = 'soft' if int(a[0]) == 0 else 'powerup'
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).node.reflection = type
                                bsInternal._getForegroundHostActivity().getMap(
                                ).node.reflectionScale = rs
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).bg.reflection = type
                                bsInternal._getForegroundHostActivity().getMap(
                                ).bg.reflectionScale = rs
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).floor.reflection = type
                                bsInternal._getForegroundHostActivity().getMap(
                                ).floor.reflectionScale = rs
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).center.reflection = type
                                bsInternal._getForegroundHostActivity().getMap(
                                ).center.reflectionScale = rs
                            except:
                                pass
                    elif m == '/shatter':
                        if a == []:
                            bsInternal._chatMessage(
                                'Using: /shatter all or number of list')
                        else:
                            if a[0] == 'all':
                                for i in bsInternal._getForegroundHostActivity(
                                ).players:
                                    i.actor.node.shattered = int(a[1])
                            else:
                                bsInternal._getForegroundHostActivity(
                                ).players[int(
                                    a[0])].actor.node.shattered = int(a[1])
                    elif m == '/cm':
                        if a == []:
                            time = 8000
                        else:
                            time = int(a[0])

                            op = 0.08
                            std = bs.getSharedObject('globals').vignetteOuter
                            bsUtils.animateArray(
                                bs.getSharedObject('globals'), 'vignetteOuter',
                                3, {
                                    0: bs.getSharedObject(
                                        'globals').vignetteOuter,
                                    17000: (0, 1, 0)
                                })

                        try:
                            bsInternal._getForegroundHostActivity().getMap(
                            ).node.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap(
                            ).bg.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap(
                            ).bg.node.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap(
                            ).node1.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap(
                            ).node2.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap(
                            ).node3.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap(
                            ).steps.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap(
                            ).floor.opacity = op
                        except:
                            pass
                        try:
                            bsInternal._getForegroundHostActivity().getMap(
                            ).center.opacity = op
                        except:
                            pass

                        def off():
                            op = 1
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).node.opacity = op
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).bg.opacity = op
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).bg.node.opacity = op
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).node1.opacity = op
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).node2.opacity = op
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).node3.opacity = op
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).steps.opacity = op
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).floor.opacity = op
                            except:
                                pass
                            try:
                                bsInternal._getForegroundHostActivity().getMap(
                                ).center.opacity = op
                            except:
                                pass
                            bsUtils.animateArray(
                                bs.getSharedObject('globals'), 'vignetteOuter',
                                3, {
                                    0: bs.getSharedObject(
                                        'globals').vignetteOuter,
                                    100: std
                                })

                        bs.gameTimer(time, bs.Call(off))

                    elif m == '/help':
                        with open(some.helpfile) as f:
                            for i in f.read().split('\n'):
                                if i != "":
                                    bsInternal._chatMessage(i)
                        bs.screenMessage('\n' * 1000)

        except:
            #bs.printException()
            pass


c = chatOptions()


def cmd(v):
    c.opt(v[0], v[1])


def lolwa():
    bs.realTimer(1000, bs.Call(bsInternal._setPartyIconAlwaysVisible, True))
    bs.realTimer(1001, lolwa)


if some.os == 'nt':
    lolwa()
with bs.Context('UI'):
    bs.realTimer(5000, bs.Call(bsInternal._setPartyIconAlwaysVisible, True))
