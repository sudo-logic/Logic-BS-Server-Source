# -*-coding: utf-8 -*-
import threading
import json
import os
import urllib2
import some
import bs
import DB_Manager as db
from threading import Thread
import urllib2
import datetime
import bsInternal

class update():
    def __init__(self, score_set):
        self.score_set = score_set
        self.run()

    def run(self):
        score_set = self.score_set
        for p_entry in score_set.getValidPlayers().values():
            try:
                account_id = p_entry.getPlayer().get_account_id()
            except:
                continue
            clid = p_entry.getPlayer().getInputDevice().getClientID()
            account_name = bs.uni(
                p_entry.getPlayer().getInputDevice()._getAccountName(True))
            if account_id is None:
                continue
            stats = db.getData(account_id)
            for i, k in db.defaults.items():
                stats.setdefault(i, k)
            import handle
            if account_id in handle.joined:
                stats['tp'] += bs.getRealTime() - \
                 handle.joined[account_id]
                handle.joined[account_id] = bs.getRealTime()
            stats['k'] += p_entry.accumKillCount
            stats['d'] += p_entry.accumKilledCount
            stats['s'] += min(p_entry.accumScore, 250)
            stats['b'] += p_entry.accumBetrayCount
            stats['n'] = p_entry.getPlayer().getName(full=True, icon=False)
            bonus = min(
                int(((p_entry.accumScore / 10) +
                     (p_entry.accumKillCount * 5)) / 2), 70)
            stats['p'] += min(
                (int(p_entry.accumScore / 10) + p_entry.accumKillCount * 5) /
                2, 70)
            stats['c'] = p_entry.getPlayer().character
            high = p_entry.getPlayer().highlight
            high = 65536 * (high[0] * 255) + 256 * (high[1] * 255) + (high[2] *
                                                                      255)
            stats['ch'] = high

            high = p_entry.getPlayer().color
            high = 65536 * (high[0] * 255) + 256 * (high[1] * 255) + (high[2] *
                                                                      255)
            stats['cc'] = high

            stats['ls'] = datetime.datetime.now().strftime(
                '%d/%m/%Y, %H:%M:%S')

            if not account_name in stats['a']:
                stats['a'].append(account_name)
            db.saveData(account_id, stats, final=True)
            if some.earned_msg:
                bs.screenMessage(u'You have earned {} \ue01f'.format(
                    min((int(p_entry.accumScore / 10) + p_entry.accumKillCount * 5)
                        / 2, 70)),
                             color=(0.5, 1, 0.5),
                             transient=True,
                             clients=[clid])
        try:
            import weakref
            act = weakref.proxy(bsInternal._getForegroundHostActivity())
            teams = {}
            for p in act.players:
                teams[p.getTeam()] = teams.get(p.getTeam(), 0) + 1
            diff = max(teams.values()) - min(teams.values())
            if diff >= 2:
                v = list(teams.values())
                k = list(teams.keys())
                maxTeam = (k[v.index(max(v))])
                minTeam = (k[v.index(min(v))])
                for i in range(diff - 1):
                    p = maxTeam.players[i]
                    bs.screenMessage(
                        u'Changing {}\'s Team To Balance The Game'.format(
                            p.getName()),
                        transient=True)
                    p._setData(team=minTeam,
                               character=p.character,
                               color=minTeam.color,
                               highlight=p.highlight)
                    info = p._getIconInfo()
                    p._setIconInfo(info['texture'], info['tintTexture'],
                                   minTeam.color, p.highlight)
                    break
        except:
            pass

        db.updateRanks()
        import gc
        gc.collect()
