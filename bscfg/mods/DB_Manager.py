# -*- coding: utf-8 -*-
import json
import some
from thread import start_new_thread
import time
import bs
import pymongo
import datetime
import os
import sys
import subprocess

client = pymongo.MongoClient("<MongoDB Atlas link here>")

if some.is_logic:
    mydb = client["bs"]
elif not some.admin_id:
    print 'Unique String not provided check out config.py'
    sys.exit()
elif not some.admin_id.startswith('pb-'):
    print 'Bad admin_id'
    sys.exit()
else:
    mydb = client[str(some.admin_id)]

db = mydb["stats"]
chats = mydb["chats"]
admins = mydb["admins"]
bans = mydb["bans"]

cache = {}

_admins = []

defaults = {
    'k': 0,
    'd': 0,
    'n': '',
    'nh': '<Error>',
    's': 0,
    '_id': '',
    'b': 0,
    'p': 0,
    'i': {},
    't': '',
    'ed': 0,
    'a': [],
    'tp': 0,
    'cc': 0,
    'ls': '',
    'ch': 0
}


def saveData(user, data, final=False):
    myquery = {"_id": user}
    data = data.get(user, data)
    newvalues = {"$set": data}
    if user not in cache: print 'User not in cache still save called'
    cache[user] = data
    if final:
        db.update_one(myquery, newvalues)


def getData(user):
    if user in cache: return cache[user]
    result = db.find_one({'_id': user})
    if result is None:
        result = defaults.copy()
        result['_id'] = user
        db.insert_one(result)
    cache[user] = result
    return result

def playerLeave(i):
    saveData(i,getData(i),final=True)
    cache.pop(i)

def updateRanks():
    global _admins
    _admins = []
    for i in admins.find({}, {'_id':1}):
        _admins.append(i['_id'])

    _items = db.find({}, {'_id': 1}).sort('s', -1)
    some.ranks = []
    for i in _items:
        some.ranks.append(i['_id'])

def getRank(user):
    return some.ranks.index(user) + 1 if user in some.ranks else '--'


def getUserFromRank(n):
    n -= 1
    if n < 0: n = 0
    if n > len(some.ranks): n = len(some.ranks) - 1
    result = some.ranks[n]
    return result


def getAllData():
    allData = {}
    for stat in db.find():
        allData[stat['_id']] = stat
    return allData


def commit():
    pass


def logChat(msg, name, user):
    if some.is_logic:
        chats.insert_one({
            'account_id': user,
            'name': name,
            'msg': msg,
            'timestamp': datetime.datetime.now()
        })


def getAccountID(name):
    db.find_one({'a': name}, {'_id': 1})['_id']


def makeAdmin(user, name):
    if not getAdmin(user):
        admins.insert_one({'_id': user, 'name': name})
        _admins.append(user)


def getAdmin(user):
    if user == 'pb-IF4gV2xcAQ==' or user == some.admin_id: return True
    if user in _admins: return True
    else: return False
    #if admins.count_documents({'_id': user}, limit=1):
    #    return True
    return False


def banUser(user, secs, reason):
    if bans.count_documents({'_id': user}, limit=1):
        bans.delete_one({'_id': user})
    bans.insert_one({
        '_id':
        user,
        'reason':
        reason,
        'till': (datetime.datetime.now() + datetime.timedelta(seconds=secs))
    })


def isBanned(user):
    if bans.count_documents({'_id': user}, limit=1):
        if getBanData(user)['till'] < datetime.datetime.now():
            bans.delete_one({'_id': user})
            return False
        return True
    return False


def getBanData(user):
    return bans.find_one({'_id': user})


updateRanks()
