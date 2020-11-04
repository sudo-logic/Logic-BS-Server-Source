# -*- coding: utf-8 -*-
import bsInternal
import bs
import some
import handle


def k(reason, id, name='Player'):
    with bs.Context('UI'):
        bs.screenMessage((u'Kicking {} | Reason: {}').format(name, reason),
                         transient=True)
        bsInternal._disconnectClient(int(id))


def kick(nick, reason='-', warn=False, mute=False, time=2):
    import ChatManager
    if '/' in nick:
        nick = nick.split('/')[0]
        #print nick.encode('unicode_escape')
    i = handle.getPlayerFromNick(nick)
    if i is not None:
        n = i.get_account_id()
        clid = i.getInputDevice().getClientID()
        name = i.getName(True)
        if mute:
            if clid not in ChatManager.mutedIDs:
                ChatManager.mutedIDs.append(clid)
            bs.screenMessage(
                u"{} Has Been Muted | Reason: {} | Muted For: {} Minutes".
                format(name, reason, time),
                transient=True)

            def unmute(clid):
                if clid in ChatManager.mutedIDs:
                    ChatManager.mutedIDs.remove(clid)

            with bs.Context('UI'):
                bs.realTimer(time * 60 * 1000, bs.Call(unmute, clid))
        if warn == True:
            if n in some.warn:
                some.warn[n] += 1
                if some.warn[n] >= 3:
                    some.banned.append(n)
                    bs.screenMessage(
                        u'Warn Limit Reached, Temporarily Banning Player',
                        transient=True)
                    k(reason, clid, name)
                    return
            else:
                some.warn.update({n: 1})
            bs.screenMessage(
                u"{} Has Been Warned | Reason: {} | Warn Count: {}/3".format(
                    name, reason, some.warn[n]),
                transient=True)
            return
        else:
            k(reason, clid, name)
            return

    roster = bsInternal._getGameRoster()

    for i in roster:
        try:
            if bs.uni(i['displayString']).lower().find(
                    bs.uni(nick).lower()) != -1 or str(i['clientID']) == nick:
                if not bs.uni(i['displayString']) == bs.uni(u'AwesomeLogic'):
                    k(reason, int(i['clientID']), bs.uni(i['displayString']))
        except Exception as e:
            print e
