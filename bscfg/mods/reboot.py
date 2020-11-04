import bs
import bsInternal
import urllib2
import bsUtils
import DB_Manager

try:
    req = urllib2.Request('http://icanhazip.com', data=None)
    response = urllib2.urlopen(req, timeout=5)
    ip = str(bs.uni(response.read())).rstrip()
except:
    ip = 'Failed To Fetch IP'
port = str(bs.getConfig().get('Port', 43210))


def restart():
    bsInternal._chatMessage('Rebooting Server... Thanks For Playing!')
    bsInternal._chatMessage('You Can Also Join Again Using IP & Port')
    text = 'IP: %s  Port: %s' % (ip, port)
    bsInternal._chatMessage(text)
    bs.realTimer(3000, bs.Call(bs.quit))


bs.realTimer(3 * 60 * 60 * 1000, restart)


def warn():
    bs.screenMessage('Server is going to reboot in 1 minute', transient=True)


bs.realTimer((3 * 60 * 60 * 1000) - 60000, warn)
