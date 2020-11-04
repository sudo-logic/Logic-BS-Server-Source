import bsInternal
import bs
import some
import handle
import DB_Manager as db

__bsInternal_disconnectClient = bsInternal._disconnectClient


def __ModifyBs_disconnectClient(clientID, Force=False, banTime=5 * 60):
    accountid = handle.getAccountIDFromClientID(clientID)
    if accountid is not None:
        if db.getAdmin(accountid):
            bs.screenMessage("Admin Detected. Aborting Kick...",
                             transient=True)
            print "%s is in Admin-List! Aborting Kick!" % accountid
            return
    __bsInternal_disconnectClient(clientID, banTime=banTime)


bsInternal._disconnectClient = bs._disconnectClient = __ModifyBs_disconnectClient
