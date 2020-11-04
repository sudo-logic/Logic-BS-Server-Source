import bsInternal
import bs
import json
import reboot
import detect
import bsUtils
import some

try:

    def lol(res):
        # print res
        if res != None:
            #print 'List Updated'
            my_data = {
                "a": reboot.ip,
                "n": bsUtils._gServerConfig.get('partyName', ''),
                "p": int(reboot.port),
                "s": detect.players_num,
                "sm": bsInternal._getPublicPartyMaxSize(),
                "sa": "https://awesomelogic.wtf/",
                "pi": 20000
            }
            res['l'].append(my_data)
            open(usd + '/ServerList.json',
                 'w+').write(json.dumps(res['l'], indent=4))

    env = bs.getEnvironment()
    usd = env['userScriptsDirectory']

    def a():
        bsInternal._addTransaction(
            {
                'type': 'PUBLIC_PARTY_QUERY',
                'proto': env['protocolVersion'],
                'lang': bs.getLanguage()
            },
            callback=lol)
        bsInternal._runTransactions()
        bs.realTimer(30000, a)

    if some.is_logic: bs.realTimer(1000, a)
except:
    pass
