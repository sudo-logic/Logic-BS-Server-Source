#!/usr/bin/python
# -*- coding: utf-8 -*-
import bs
import os
import sys
p = os.path.abspath(bs.getEnvironment()['userScriptsDirectory'])
data = {}

auto = False


def update():
    try:
        for i in os.listdir(p):
            if i.endswith('.py') and i != 'autoreload.py':
                mtime = os.path.getmtime(os.path.join(p, i))
                if not i in data:
                    data[i] = mtime
                    bs.screenMessage('New script added.', transient=True)
                if data[i] != mtime:
                    print 'Reloading:', i
                    bs.screenMessage('New changes detected, reloading script',
                                     transient=True)
                    module = __import__(''.join(i[:-3]))
                    reload(module)
                    data[i] = mtime
    except Exception, e:
        print e
        bs.screenMessage(repr(e), transient=True)
    if auto:
        bs.realTimer(5000, update)


bs.realTimer(5000, update)
