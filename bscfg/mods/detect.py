# -*- coding: utf-8 -*-
import bs
import bsInternal
import time
import threading
import some
banned = []
old = []
maxPlayers = 0
players_num = 0
config_maxPlayers = 0


def run():
    try:
        global old
        global maxPlayers
        global players_num
        roster = bsInternal._getGameRoster()
        players_num = len(roster) if len(roster) != 0 else 1
        bsInternal._setPublicPartyMaxSize(
            min(max(9,
                    len(roster) + 1), maxPlayers))
        global banned
        banned = some.banned
        if roster != old:
            for i in roster:
                a = bs.uni(i['displayString'])
                # print a
                if a in banned:
                    with bs.Context('UI'):
                        bs.screenMessage(
                            "You Have Been Banned. If The Ban Is Temporary, Try Joining After Some Time.",
                            transient=True,
                            clients=[int(i['clientID'])])
                    bsInternal._disconnectClient(int(i['clientID']))
                if eval(i['specString'])["a"] in [
                        '', 'Server'
                ] and int(i['clientID']) != -1:
                    with bs.Context('UI'):
                        bs.screenMessage("Please Sign In and Join",
                                         transient=True,
                                         clients=[int(i['clientID'])])
                    bsInternal._disconnectClient(int(i['clientID']))
            old = roster
    except Exception as e:
        pass
    bs.realTimer(2000, run)


def setmax():
    global maxPlayers
    global config_maxPlayers
    maxPlayers = bsInternal._getPublicPartyMaxSize()
    config_maxPlayers = maxPlayers


def reset():
    global maxPlayers
    maxPlayers = config_maxPlayers


bs.realTimer(1500, setmax)
bs.realTimer(2000, run)
