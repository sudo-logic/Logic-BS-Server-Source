import bs
import urllib2
import json
import bsInternal
import some
import random
import time as tim
import DB_Manager as db
import mystats
import datetime
import requests
celeb = [
    'Narendra Modi', 'PewDiePie', 'Mr Beast', 'AwesomeLogic', 'John Cena',
    'Anonymous', 'Donald Trump', 'Your GirlFriend', 'Yo mama',
    'Someone you don\'t know', 'Your son', 'Eric Froemling', 'Your dad',
    'Another begger', 'That ass who keeps begging for admin'
]

time = {}
joined = {}

queue = []

def join(accountid,clientID):
    if accountid is not None and clientID is not None:
        if db.isBanned(accountid):
            data = db.getBanData(accountid)
            bs.screenMessage(
                "You have been banned. Ban Expires on: {} IST".format(
                    data['till'].strftime('%Y/%m/%d %H:%M:%S')),
                color=(1, 0, 0),
                clients=[clientID],
                transient=True)
            bsInternal._disconnectClient(clientID)
            return
        joined.update({accountid: bs.getRealTime()})
        now_time = long(tim.strftime('%Y%m%d%H%M', tim.localtime(tim.time())))
        stats = db.getData(accountid)
        if stats['i'] == []:
            stats['i'] = {}
        for name, exp in stats['i'].items():
            if now_time > exp:
                bs.screenMessage(
                    '%s Expired' % name,
                    clients=[clientID],
                    transient=True)
                stats['i'].pop(name)
        db.saveData(accountid, stats)
        daily(accountid,clientID)
    queue.remove(accountid)


def daily(n,n2):
    if n is None:
        return
    date = int(datetime.datetime.now().strftime('%d'))
    stats = db.getData(n)
    if stats.get('ed', 0) != date:
        stats['p'] += 50
        stats['ed'] = date
        bs.screenMessage(u"You Got 50 \ue01f Daily Bonus",
                         clients=[n2],
                         transient=True)
        db.saveData(n, stats)
    return


def inv(nick):
    n = nick.get_account_id()
    clid = nick.getInputDevice().getClientID()
    stats = db.getData(n)
    items = stats['i']
    import datetime
    msgs = []
    msgs.append('You currently have {} items'.format(len(items)))
    for i, e in items.items():
        expire = datetime.datetime.strptime(
            str(e), "%Y%m%d%H%M").strftime("%d-%m-%Y %H:%M:%S")
        msgs.append('Item: {} | Expires On: {}'.format(i.upper(), expire))
    bs.screenMessage('\n'.join(msgs),
                     transient=True,
                     clients=[clid],
                     color=(0.7, 0.7, 1))


def me(nick):
    if nick is None:
        return
    if isinstance(nick, bs.Player):
        n = nick.get_account_id()
    elif nick.startswith('pb'):
        n = nick
    else:
        return
    stats = db.getData(n)
    score = stats['s']
    rank = db.getRank(n)
    points = stats['p']
    message = bs.uni(stats['n'])
    message2 = u'\ue01f: ' + str(points)
    message3 = 'Total Score: ' + str(score)
    message4 = 'Rank: ' + str(rank)
    message5 = 'K: ' + str(stats['k'])
    message6 = 'D: ' + str(stats['d'])
    if n in joined:
        message7 = 'Time Spent: ' + str(
            datetime.timedelta(milliseconds=(bs.getRealTime() -
                                             joined[str(n)] +
                                             stats['tp']))).split('.', 2)[0]
    else:
        message7 = 'Time Spent: ' + \
            str(datetime.timedelta(milliseconds=(
                stats['tp']))).split('.', 2)[0]
    bs.screenMessage(u'  |  '.join(
        [message, message2, message3, message4, message5, message6, message7]))
    clear(2500)


def getPlayerFromNick(nick):
    nick = bs.uni(nick[:-3] if nick.endswith('...') else nick)
    if '/' in nick:
        nick = nick.split('/')[0]
    if nick.isdigit():
        if len(nick) == 3:
            for i in bsInternal._getForegroundHostActivity().players:
                if str(i.getInputDevice().getClientID()) == nick:
                    return i
        if int(nick) < len(bsInternal._getForegroundHostActivity().players):
            return bsInternal._getForegroundHostActivity().players[int(nick)]
    else:
        for i in bsInternal._getForegroundHostActivity().players:
            if i.getName(True).lower().find(nick.lower()) != -1:
                return i
        else:
            return None


def give(p, nick, amount, reason):
    try:
        amount = abs(int(amount))
    except:
        return
    giver = p.get_account_id()
    taker_player = getPlayerFromNick(nick)
    if taker_player is None:
        return
    taker = taker_player.get_account_id()
    if taker == giver:
        bs.screenMessage(
            'Why would you try to give yourself tickets!\nStoopid Ass')
        return
    g = db.getData(giver)
    t = db.getData(taker)
    if not g['p'] >= amount:
        return
    g['p'] -= amount
    db.saveData(giver, g)
    t['p'] += amount
    db.saveData(taker, t)
    reason = reason if reason != '' else 'Gift :>'
    bs.screenMessage(u'Success | {} > {}\ue01f > {} | Reason: {}'.format(
        p.getName(True), amount, taker_player.getName(True), reason),
                     transient=True,
                     color=(0.5, 1, 0.5))

def take(p, nick, amount, reason):
    try:
        amount = abs(int(amount))
    except:
        return
    if not p.get_account_id() in [some.ownerid,some.admin_id]: bs.screenMessage('You are not the host'); return
    taker_player = getPlayerFromNick(nick)
    taker = taker_player.get_account_id()
    t = db.getData(taker)
    t['p'] -= amount
    db.saveData(taker, t)
    reason = reason if reason != '' else 'Penalty'
    bs.screenMessage(u'{} lost {}\ue01f | Reason: {}'.format(
        taker_player.getName(True), amount, reason),
                     transient=True,
                     color=(1, 0.5, 0.5))


def bet(i, amt):
    bs.screenMessage('Dangerous command, turned off for your safety.')
    return
    n = i.get_account_id()
    n2 = i.getInputDevice().getClientID()
    stats = db.getData(n)
    multiplier = 1.7 if 'multiplier' in stats['i'] else 1.3
    try:
        amt = abs(int(amt))
    except:
        if amt == 'all':
            amt = stats['p']
        elif amt == 'half':
            amt = stats['p'] // 2
        else:
            bs.screenMessage(
                'Hey Everyone! This doofus thinks "{}" is a number! Lol what a noob'
                .format(amt),
                color=(1, 0, 0))
            return
    if stats['p'] < amt:
        bs.screenMessage('You don\'t have enough money lol. RIP. :)',
                         color=(1, .2, .2))
    else:
        bet_num = random.random()
        if bet_num <= 0:  #(0.33 if 'luckycharm' in stats['i'] else 0.25):
            stats['p'] += int(amt * multiplier)
            bs.screenMessage(u'Yaay! You won {} \ue01f'.format(
                int(amt * multiplier)),
                             color=(.5, 1, .5))
        else:
            stats['p'] -= amt
            bs.screenMessage(
                u'Lol sucks to be you. You lost {} \ue01f'.format(amt),
                color=(1, .2, .2))
        db.saveData(n, stats)


def beg(i):
    n = i.get_account_id()
    n2 = i.getInputDevice().getClientID()
    stuff = db.getData(n)
    prob = random.random()
    if prob >= 0.2:
        c = random.randint(5, 25)
        stuff['p'] += c
        db.saveData(n, stuff)
        bsInternal._chatMessage(
            random.choice(celeb) + ' Gave ' + i.getName(full=True) + ' ' +
            str(c) + u" \ue01f!")
    else:
        bs.screenMessage(random.choice(celeb) + " flicked " +
                         i.getName(full=True) + ' off!',
                         color=(1, 0, 0),
                         transient=True)
    clear()


def convert(i, amount):
    n = i.get_account_id()
    n2 = i.getInputDevice().getClientID()
    stats = db.getData(n)
    try:
        amount = abs(int(amount))
    except:
        pass
    if amount >= 10000:
        bs.screenMessage('You wanna be hella rich or whut?')
        return
    if amount <= stats['s']:
        stats['s'] -= amount
        stats['p'] += int(amount / 10)
        bs.screenMessage(
            u'{} Score Points have been converted to {} \ue01f'.format(
                amount, int(amount / 10)))
        bs.screenMessage(u'New Score: {} | New \ue01f: {}'.format(
            stats['s'], stats['p']))
        db.saveData(n, stats)
    else:
        bs.screenMessage('Not Enough Score Points',
                         clients=[n2],
                         transient=True,
                         color=(1, 0.5, 0.5))


def joke(name):
    categories = [
        "animal", "career", "celebrity", "dev", "fashion", "food", "history",
        "money", "movie", "music", "political", "religion", "science", "sport",
        "travel"
    ]
    joke_json = requests.get(
        'https://api.chucknorris.io/jokes/random?name=XDXDXD&category={}'.
        format(','.join(categories))).json()
    bsInternal._chatMessage(joke_json['value'].replace('XDXDXD', name))
    bs.callInGameThread(bs.Call(clear, 500))


def getAccountNamesFromAccountID(nick):
    accs = db.getData(nick)['a']
    return accs


def getAccountIDFromAccountName(id):
    return db.getAccountID(id)


def getAccountIDFromClientID(clientID):
    for i in bsInternal._getForegroundHostActivity().players:
        if i.getInputDevice().getClientID() == clientID:
            return i.get_account_id()
    else:
        return None


def clear(time=1500):
    with bs.Context('UI'):
        bs.realTimer(time,
                     bs.Call(bs.screenMessage, '\n' * 1000, transient=True))
