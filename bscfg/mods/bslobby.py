# -*- coding: utf-8 -*-
import bs
import bsLobby
import some
import bs
import bsUtils
import bsSpaz
import random
import weakref
import bsUI
import bsInternal
import ast
import json
from bsLobby import *
import handle
import DB_Manager as db

gRandProfileIndex = 1
gLastWarnTime = 0
gRandomCharIndexOffset = None

change_limit = 10

ChangeMessage = bsLobby.ChangeMessage


def _setReady(self, ready):

    import bsInternal

    profileName = self.profileNames[self.profileIndex]

    # handle '_edit' as a special case
    if profileName == '_edit' and ready:
        import bsUI
        with bs.Context('UI'):
            bsUI.PlayerProfilesWindow(inMainMenu=False)
            # give their input-device UI ownership too
            # (prevent someone else from snatching it in crowded games)
            bsInternal._setUIInputDevice(self._player.getInputDevice())
        return

    if ready == False:
        self._player.assignInputCall(
            'leftPress', bs.Call(self.handleMessage, ChangeMessage('team',
                                                                   -1)))
        self._player.assignInputCall(
            'rightPress', bs.Call(self.handleMessage, ChangeMessage('team',
                                                                    1)))
        self._player.assignInputCall(
            'bombPress',
            bs.Call(self.handleMessage, ChangeMessage('character', 1)))
        self._player.assignInputCall(
            'upPress',
            bs.Call(self.handleMessage, ChangeMessage('profileIndex', -1)))
        self._player.assignInputCall(
            'downPress',
            bs.Call(self.handleMessage, ChangeMessage('profileIndex', 1)))
        self._player.assignInputCall(
            ('jumpPress', 'pickUpPress', 'punchPress'),
            bs.Call(self.handleMessage, ChangeMessage('ready', 1)))
        self.ready = False
        self._updateText()
        self._player.setName('untitled', real=False)
    elif ready == True:
        self._player.assignInputCall(
            ('leftPress', 'rightPress', 'upPress', 'downPress', 'jumpPress',
             'bombPress', 'pickUpPress'), self._doNothing)
        self._player.assignInputCall(
            'upPress', bs.Call(self.handleMessage, ChangeMessage('screen',
                                                                 -1)))
        self._player.assignInputCall(
            'downPress', bs.Call(self.handleMessage,
                                 ChangeMessage('screen', 1)))
        self._player.assignInputCall(
            'bombPress', bs.Call(self.handleMessage, ChangeMessage('ready',
                                                                   0)))
        self._player.assignInputCall(
            ('jumpPress', 'pickUpPress', 'punchPress'),
            bs.Call(self.handleMessage, ChangeMessage('ready', 2)))
        # store the last profile picked by this input for reuse
        inputDevice = self._player.getInputDevice()
        name = inputDevice.getName()
        uniqueID = inputDevice.getUniqueIdentifier()
        try:
            deviceProfiles = bs.getConfig()['Default Player Profiles']
        except Exception:
            deviceProfiles = bs.getConfig()['Default Player Profiles'] = {}

        # make an exception if we have no custom profiles and are set
        # to random; in that case we'll want to start picking up custom
        # profiles if/when one is made so keep our setting cleared
        haveCustomProfiles = (True if [
            p for p in self.profiles
            if p not in ('_random', '_edit', '__account__')
        ] else False)
        if profileName == '_random' and not haveCustomProfiles:
            try:
                del (deviceProfiles[name + ' ' + uniqueID])
            except Exception:
                pass
        else:
            deviceProfiles[name + ' ' + uniqueID] = profileName
        bs.writeConfig()

        # set this player's short and full name
        # self._player.setName(self._getName(full=True,clamp=True).replace("'"," ").replace('"',' '),
        #                     self._getName(full=True,clamp=False).replace("'"," ").replace('"',' '),
        #                     real=True)
        self._player.setName(self._getName(full=True, clamp=True),
                             self._getName(full=True, clamp=False),
                             real=True)
        self.ready = True
        self._updateText()
    else:
        if self.screen == 'join':
            bs.getSession().handleMessage(PlayerReadyMessage(self))
        elif self.screen == 'stats':
            if bs.getGameTime() - self.statsTime >= 7000:
                n = self._player.get_account_id()
                clid = self._player.getInputDevice().getClientID()
                self.statsTime = bs.getGameTime()
                if n is None:
                    return
                handle.me(self._player)
            self.screen = 'join'
            self._updateText()


def handleMessage(self, msg):

    if isinstance(msg, ChangeMessage):

        # if we've been removed from the lobby, ignore this stuff
        if msg.what == 'team' and not self._admin:
            self.change_count += 1
            if self.change_count > change_limit -5:
                bs.screenMessage(
                    'Spam Detected! Warn Count: {}/5'.format(
                        self.change_count-(change_limit-5)),
                    clients=[self._player.getInputDevice().getClientID()],
                    color=(1, 0.2, 0.2),
                    transient=True)
            if self.change_count >= change_limit:
                bs.screenMessage('Lobby Spammer Get Rekt!',
                                 color=(1, 0.2, 0.2),
                                 transient=True)
                bsInternal._disconnectClient(
                    self._player.getInputDevice().getClientID())
        if self._dead:
            print "WARNING: chooser got ChangeMessage after dying"
            return

        if not self._textNode.exists():
            bs.printError('got ChangeMessage after nodes died')
            return
        if msg.what == 'screen':
            self.screen = self.screens[(
                (self.screens.index(self.screen) + msg.value) %
                len(self.screens))]
            self._updateText()
        if msg.what == 'team':
            if len(self.getLobby()._teams) > 1:
                bs.playSound(self._swishSound)
            self._selectedTeamIndex = ((self._selectedTeamIndex + msg.value) %
                                       len(self.getLobby()._teams))
            self._updateText()
            self.updatePosition()
            self._updateIcon()

        elif msg.what == 'profileIndex':
            if len(self.profileNames) == 1:
                # this should be pretty hard to hit now with
                # automatic local accounts..
                bs.playSound(bs.getSound('error'))
            else:
                # pick the next player profile and assign our name
                # and character based on that
                bs.playSound(self._deekSound)
                self.profileIndex = ((self.profileIndex + msg.value) %
                                     len(self.profileNames))
                self.updateFromPlayerProfile()

        elif msg.what == 'character':
            bs.playSound(self._clickSound)
            # update our index in our local list of characters
            self.characterIndex = ((self.characterIndex + msg.value) %
                                   len(self.characterNames))
            # bs.screenMessage(self.characterNames[self.characterIndex])
            self._updateText()
            self._updateIcon()

        elif msg.what == 'ready':
            forceTeamSwitch = False
            # team auto-balance kicks us to another team if we try to
            # join the team with the most players
            if not self.ready:
                if bs.getConfig().get('Auto Balance Teams', False):
                    lobby = self.getLobby()
                    if len(lobby._teams) > 1:
                        session = bs.getSession()
                        # first, calc how many players are on each team
                        # ..we need to count both active players and
                        # choosers that have been marked as ready.
                        teamPlayerCounts = {}
                        for team in lobby._teams:
                            teamPlayerCounts[team().getID()] = \
                                len(team().players)
                        for chooser in lobby.choosers:
                            if chooser.ready:
                                teamPlayerCounts[
                                    chooser.getTeam().getID()] += 1
                        largestTeamSize = max(teamPlayerCounts.values())
                        smallestTeamSize = \
                            min(teamPlayerCounts.values())
                        # force switch if we're on the biggest team
                        # and there's a smaller one available
                        if (largestTeamSize != smallestTeamSize
                                and teamPlayerCounts[self.getTeam().getID()] >=
                                largestTeamSize):
                            forceTeamSwitch = True

            if forceTeamSwitch:
                bs.playSound(self._errorSound)
                self.handleMessage(ChangeMessage('team', 1))
                bs.screenMessage(
                    "Unequal Teams!",
                    color=(0.8, 0.5, 0.2),
                    clients=[self._player.getInputDevice().getClientID()],
                    transient=True)
            else:
                if msg.value != 2:
                    bs.playSound(self._punchSound)
                self._setReady(msg.value)


def _updateText(self):

    if self.ready:
        # once we're ready, we've saved the name, so lets ask the system
        # for it so we get appended numbers and stuff
        text = bs.Lstr(value=self._player.getName(full=True))
        if self.screen == 'join':
            text = bs.Lstr(value='${A} ${B}',
                           subs=[('${A}', text),
                                 ('${B}', bs.Lstr(value=u'> 🎮 Join Game 🎮'))])
        elif self.screen == 'stats':
            text = bs.Lstr(value='${A} ${B}',
                           subs=[('${A}', text),
                                 ('${B}', bs.Lstr(value=u'> 📈 Stats 📉'))])
    else:
        text = bs.Lstr(value=self._getName(full=True))

    canSwitchTeams = len(self.getLobby()._teams) > 1

    # flash as we're coming in
    finColor = bs.getSafeColor(self.getColor()) + (1, )
    if not self._inited:
        bsUtils.animateArray(self._textNode, 'color', 4, {
            150: finColor,
            250: (2, 2, 2, 1),
            350: finColor
        })
    else:
        # blend if we're in teams mode; switch instantly otherwise
        if canSwitchTeams:
            bsUtils.animateArray(self._textNode, 'color', 4, {
                0: self._textNode.color,
                100: finColor
            })
        else:
            self._textNode.color = finColor

    self._textNode.text = text


def __init__(self, vPos, player, lobby):

    import bsInternal

    self._deekSound = bs.getSound('deek')
    self._clickSound = bs.getSound('click01')
    self._punchSound = bs.getSound('punch01')
    self._swishSound = bs.getSound('punchSwish')
    self._errorSound = bs.getSound('error')
    self._maskTexture = bs.getTexture('characterIconMask')
    self._vPos = vPos
    self._lobby = weakref.ref(lobby)
    self._player = player
    self.change_count = 0
    self._inited = False
    self._dead = False
    self._admin = db.getAdmin(self._player.get_account_id())

    # load available profiles either from the local config or from the
    # remote device..
    self.reloadProfiles()

    # note: this is just our local index out of available teams; *not*
    # the team ID!
    self._selectedTeamIndex = self.getLobby().nextAddTeam

    # store a persistent random character index; we'll use this for the
    # '_random' profile. Let's use their inputDevice id to seed it.. this
    # will give a persistent character for them between games and will
    # distribute characters nicely if everyone is random
    try:
        inputDeviceID = self._player.getInputDevice().getID()
    except Exception as e:
        print 'ERROR: exc getting inputDeviceID for chooser creation:', e
        inputDeviceID = 0
        import traceback
        traceback.print_stack()

    # we want the first device that asks for a chooser to always get
    # spaz as a random character..
    global gRandomCharIndexOffset
    if gRandomCharIndexOffset is None:
        # scratch that.. we now kinda accomplish the same thing with
        # account profiles so lets just be fully random here..
        gRandomCharIndexOffset = random.randrange(1000)

    # to calc our random index we pick a random character out of our
    # unlocked list and then locate that character's index in the full list

    self._randomCharacterIndex = ((inputDeviceID + gRandomCharIndexOffset) %
                                  len(self.characterNames))

    self._randomColor, self._randomHighlight = \
        bsUtils.getPlayerProfileColors(None)
    global gAccountProfileDeviceID
    # attempt to pick an initial profile based on what's been stored
    # for this input device
    try:
        inputDevice = self._player.getInputDevice()
        name = inputDevice.getName()
        uniqueID = inputDevice.getUniqueIdentifier()
        self.profileName = (
            bs.getConfig()['Default Player Profiles'][name + ' ' + uniqueID])
        self.profileIndex = self.profileNames.index(self.profileName)

        # if this one is __account__ and is local and we havn't marked
        # anyone as the account-profile device yet, mark this guy as it.
        # (prevents the next joiner from getting the account profile too)
        if (self.profileName == '__account__'
                and not inputDevice.isRemoteClient()
                and gAccountProfileDeviceID is None):
            gAccountProfileDeviceID = inputDeviceID

    # well hmm that didn't work.. pick __account__, _random, or some
    # other random profile..
    except Exception:

        profileNames = self.profileNames

        # we want the first local input-device in the game to latch on to
        # the account profile
        if (not inputDevice.isRemoteClient()
                and not inputDevice.isControllerApp()):
            if (gAccountProfileDeviceID is None
                    and '__account__' in profileNames):
                gAccountProfileDeviceID = inputDeviceID

        # if this is the designated account-profile-device, try to default
        # to the account profile
        if (inputDeviceID == gAccountProfileDeviceID
                and '__account__' in profileNames):
            self.profileIndex = profileNames.index('__account__')
        else:
            # if this is the controller app, it defaults to using a random
            # profile (since we can pull the random name from the app)
            if inputDevice.isControllerApp():
                self.profileIndex = profileNames.index('_random')
            else:
                # if its a client connection, for now just force the account
                # profile if possible.. (need to provide a way for clients
                # to specify/remember their default profile)
                if (inputDevice.isRemoteClient()
                        and '__account__' in profileNames):
                    self.profileIndex = profileNames.index('__account__')
                else:
                    global gRandProfileIndex
                    # cycle through our non-random profiles once; after
                    # that, everyone gets random.
                    while (gRandProfileIndex < len(profileNames)
                           and profileNames[gRandProfileIndex]
                           in ('_random', '__account__', '_edit')):
                        gRandProfileIndex += 1
                    if gRandProfileIndex < len(profileNames):
                        self.profileIndex = gRandProfileIndex
                        gRandProfileIndex += 1
                    else:
                        self.profileIndex = profileNames.index('_random')

        self.profileName = profileNames[self.profileIndex]

    self.characterIndex = self._randomCharacterIndex
    self._color = self._randomColor
    self._highlight = self._randomHighlight
    self.ready = False
    self.statsTime = 0
    self.screen = 'join'
    self.screens = ['join', 'stats']
    self._textNode = bs.newNode('text',
                                delegate=self,
                                attrs={
                                    'position': (-100, self._vPos),
                                    'maxWidth': 160,
                                    'shadow': 0.5,
                                    'vrDepth': -20,
                                    'hAlign': 'left',
                                    'vAlign': 'center',
                                    'vAttach': 'top'
                                })

    bsUtils.animate(self._textNode, 'scale', {0: 0, 300: 1.0})
    bs.animate(self._textNode, 'rotate', {0: 0.0, 300: 360.0}, loop=False)
    self.icon = bs.newNode('image',
                           owner=self._textNode,
                           attrs={
                               'position': (-130, self._vPos + 20),
                               'maskTexture': self._maskTexture,
                               'vrDepth': -10,
                               'attach': 'topCenter'
                           })

    bsUtils.animateArray(self.icon, 'scale', 2, {0: (0, 0), 500: (45, 45)})
    bs.animate(self.icon, 'rotate', {0: 0.0, 500: 360.0}, loop=False)

    self._setReady(False)

    # set our initial name to '<choosing player>' in case anyone asks..
    self._player.setName(bs.Lstr(resource='choosingPlayerText').evaluate(),
                         real=False)

    self.updateFromPlayerProfile()
    try:
        self.loadAllCharacters()
    except:
        pass
    self.updatePosition()
    self._inited = True


def loadAllCharacters(self):
    account_id = self._player.get_account_id()
    if account_id is None:
        return
    items = db.getData(account_id)['i']
    if items is not None:
        if isinstance(getattr(self, "characterNames", None), list):
            try:
                if 'unlock-chars' in items:
                    self.characterNames.append('Steve')
                    self.characterNames.append('Raphael')
                    # for name,profile in self.profiles.items():
                    #     character = profile.get("character","Spaz")
                    #     if (character not in self.characterNames
                    #             and character in bsSpaz.appearances):
                    #         self.characterNames.append(character)
                    for i, k in bsSpaz.appearances.items():
                        if k.style != 'spaz' and i not in self.characterNames:
                            self.characterNames.append(i)
                    bs.screenMessage(
                        'All Characters Unlocked',
                        color=(0, 1, 0),
                        clients=[self._player.getInputDevice().getClientID()],
                        transient=True)
                elif 'logicon' in items:
                    self.characterNames.append('Logicon')
                    bs.screenMessage(
                        'Logicon Unlocked',
                        color=(0, 1, 0),
                        clients=[self._player.getInputDevice().getClientID()],
                        transient=True)
            except:
                bs.printException()


def _getName(self, full=True, clamp=False):
    nameRaw = name = self.profileNames[self.profileIndex]
    if name == '_random':
        try:
            inputDevice = self._player.getInputDevice()
        except Exception:
            inputDevice = None
        if inputDevice is not None:
            name = inputDevice._getDefaultPlayerName()
        else:
            name = 'Invalid'
        if not full:
            clamp = True
    elif name == '__account__':
        try:
            inputDevice = self._player.getInputDevice()
        except Exception:
            inputDevice = None
        if inputDevice is not None:
            name = inputDevice._getAccountName(full)
        else:
            name = 'Invalid'
        if not full:
            clamp = True
    elif name == '_edit':
        # FIXME - this causes problems as an Lstr, but its ok to
        # explicitly translate for now since this is only shown on the host.
        name = (bs.Lstr(
            resource='createEditPlayerText',
            fallbackResource='editProfileWindow.titleNewText').evaluate())
    else:
        # if we have a regular profile marked as global with an icon,
        # use it (for full only)
        if full:
            try:
                if self.profiles[nameRaw].get('global', False):
                    icon = (bs.uni(
                        self.profiles[nameRaw]['icon'] if 'icon' in
                        self.profiles[nameRaw] else bs.getSpecialChar('logo')))
                    name = icon + name
            except Exception:
                bs.printException('Error applying global icon')
        else:
            # we now clamp non-full versions of names so there's at
            # least some hope of reading them in-game
            clamp = True

    if clamp:
        # in python < 3.5 some unicode chars can have length 2, so we need
        # to convert to raw int vals for safe trimming
        nameChars = bs.uniToInts(name)
        if len(nameChars) > 10:
            name = bs.uniFromInts(nameChars[:10]) + '...'
    # return 'INVALID NAME' if name.encode('ascii','ignore') == '' else name
    return name


bsLobby.Chooser.__init__ = __init__
bsLobby.Chooser._setReady = _setReady
bsLobby.Chooser._getName = _getName
bsLobby.Chooser._updateText = _updateText
bsLobby.Chooser.handleMessage = handleMessage
bsLobby.Chooser.loadAllCharacters = loadAllCharacters
