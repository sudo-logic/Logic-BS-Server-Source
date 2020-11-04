# Maded by Froshlee14
import bsSpaz
import bs
import random
import bsUtils


class Icon(bs.Actor):
    def __init__(self,
                 player,
                 position,
                 scale,
                 showLives=True,
                 showDeath=True,
                 nameScale=1.0,
                 nameMaxWidth=115.0,
                 flatness=1.0,
                 shadow=1.0):
        bs.Actor.__init__(self)
        self._player = player
        self._showLives = showLives
        self._showDeath = showDeath
        self._nameScale = nameScale

        self._outlineTex = bs.getTexture('characterIconMask')

        icon = player.getIcon()
        self.node = bs.newNode('image',
                               owner=self,
                               attrs={
                                   'texture': icon['texture'],
                                   'tintTexture': icon['tintTexture'],
                                   'tintColor': icon['tintColor'],
                                   'vrDepth': 400,
                                   'tint2Color': icon['tint2Color'],
                                   'maskTexture': self._outlineTex,
                                   'opacity': 1.0,
                                   'absoluteScale': True,
                                   'attach': 'bottomCenter'
                               })
        self._nameText = bs.newNode('text',
                                    owner=self.node,
                                    attrs={
                                        'text':
                                        bs.Lstr(value=player.getName()),
                                        'color':
                                        bs.getSafeColor(
                                            player.getTeam().color),
                                        'hAlign':
                                        'center',
                                        'vAlign':
                                        'center',
                                        'vrDepth':
                                        410,
                                        'maxWidth':
                                        nameMaxWidth,
                                        'shadow':
                                        shadow,
                                        'flatness':
                                        flatness,
                                        'hAttach':
                                        'center',
                                        'vAttach':
                                        'bottom'
                                    })
        if self._showLives:
            self._livesText = bs.newNode('text',
                                         owner=self.node,
                                         attrs={
                                             'text': 'x0',
                                             'color': (1, 1, 0.5),
                                             'hAlign': 'left',
                                             'vrDepth': 430,
                                             'shadow': 1.0,
                                             'flatness': 1.0,
                                             'hAttach': 'center',
                                             'vAttach': 'bottom'
                                         })
        self.setPositionAndScale(position, scale)

    def setPositionAndScale(self, position, scale):
        self.node.position = position
        self.node.scale = [70.0 * scale]
        self._nameText.position = (position[0], position[1] + scale * 52.0)
        self._nameText.scale = 1.0 * scale * self._nameScale
        if self._showLives:
            self._livesText.position = (position[0] + scale * 10.0,
                                        position[1] - scale * 43.0)
            self._livesText.scale = 1.0 * scale

    def updateForLives(self):
        if self._player.exists():
            lives = self._player.gameData['lives']
        else:
            lives = 0
        if self._showLives:
            if lives > 0:
                self._livesText.text = 'x' + str(lives - 1)
            else:
                self._livesText.text = ''
        if lives == 0:
            self._nameText.opacity = 0.2
            self.node.color = (0.7, 0.3, 0.3)
            self.node.opacity = 0.2

    def handlePlayerSpawned(self):
        if not self.node.exists():
            return
        self.node.opacity = 1.0
        self.updateForLives()

    def handlePlayerDied(self):
        if not self.node.exists():
            return
        if self._showDeath:
            bs.animate(
                self.node, 'opacity', {
                    0: 1.0,
                    50: 0.0,
                    100: 1.0,
                    150: 0.0,
                    200: 1.0,
                    250: 0.0,
                    300: 1.0,
                    350: 0.0,
                    400: 1.0,
                    450: 0.0,
                    500: 1.0,
                    550: 0.2
                })
            lives = self._player.gameData['lives']
            if lives == 0:
                bs.gameTimer(600, self.updateForLives)


def bsGetAPIVersion():
    return 4


def bsGetGames():
    return [SafeZoneGame]


class SafeZoneGame(bs.TeamGameActivity):
    @classmethod
    def getName(cls):
        return 'PUBG'

    @classmethod
    def getDescription(cls, sessionType):
        return 'Get To The Safe Zone!!'

    @classmethod
    def getScoreInfo(cls):
        return {
            'scoreName': 'Survived',
            'scoreType': 'seconds',
            'noneIsWinner': True
        }

    @classmethod
    def supportsSessionType(cls, sessionType):
        return True if (issubclass(sessionType, bs.TeamsSession) or issubclass(
            sessionType, bs.FreeForAllSession)) else False

    @classmethod
    def getSupportedMaps(cls, sessionType):
        return ['Football Stadium', 'Hockey Stadium']

    @classmethod
    def getSettings(cls, sessionType):
        return [("Time Limit", {
            'choices': [('None', 0), ('1 Minute', 60), ('2 Minutes', 120),
                        ('5 Minutes', 300), ('10 Minutes', 600),
                        ('20 Minutes', 1200)],
            'default':
            0
        }),
                ("Lives Per Player", {
                    'default': 2,
                    'minValue': 1,
                    'maxValue': 10,
                    'increment': 1
                }),
                ("Respawn Times", {
                    'choices': [('Short', 0.5), ('Normal', 1.0)],
                    'default': 1.0
                }), ("Epic Mode", {
                    'default': False
                }), ("Balance Total Lives", {
                    'default': True
                })]

    def __init__(self, settings):
        bs.TeamGameActivity.__init__(self, settings)
        if self.settings['Epic Mode']:
            self._isSlowMotion = True
        self._tickSound = bs.getSound('tick')
        self.announcePlayerDeaths = True

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(
            self, music='Epic' if self.settings['Epic Mode'] else 'Survival')
        self._startGameTime = bs.getGameTime()

    def onTeamJoin(self, team):
        team.gameData['survivalSeconds'] = None
        team.gameData['spawnOrder'] = []

    def onPlayerJoin(self, player):
        if self.hasBegun():
            player.gameData['lives'] = 0
            player.gameData['icons'] = []
            if self._getTotalTeamLives(player.getTeam(
            )) == 0 and player.getTeam().gameData['survivalSeconds'] is None:
                player.getTeam().gameData['survivalSeconds'] = 0
            bs.screenMessage(bs.Lstr(resource='playerDelayedJoinText',
                                     subs=[('${PLAYER}',
                                            player.getName(full=True))]),
                             color=(0, 1, 0))
            return

        player.gameData['lives'] = self.settings['Lives Per Player']

        player.gameData['icons'] = [Icon(player, position=(0, 50), scale=0.8)]
        if player.gameData['lives'] > 0:
            self.spawnPlayer(player)

        if self.hasBegun():
            self._updateIcons()

    def showInfo(playGong=True):
        activity = bs.getActivity()
        name = activity.getInstanceDisplayString()
        bsUtils.ZoomText(name,
                         maxWidth=800,
                         lifespan=2500,
                         jitter=2.0,
                         position=(0, 0),
                         flash=False,
                         color=(0.93 * 1.25, 0.9 * 1.25, 1.0 * 1.25),
                         trailColor=(0.15, 0.05, 1.0, 0.0)).autoRetain()
        if playGong:
            bs.gameTimer(200, bs.Call(bs.playSound, bs.getSound('gong')))

        desc = activity.getInstanceDescription()
        if type(desc) in [unicode, str]:
            desc = [desc]  # handle simple string case
        if type(desc[0]) not in [unicode, str]:
            raise Exception("Invalid format for instance description")
        subs = []
        for i in range(len(desc) - 1):
            subs.append(('${ARG' + str(i + 1) + '}', str(desc[i + 1])))
        translation = bs.Lstr(translate=('gameDescriptions', desc[0]),
                              subs=subs)

        if ('Epic Mode' in activity.settings
                and activity.settings['Epic Mode']):
            translation = bs.Lstr(resource='epicDescriptionFilterText',
                                  subs=[('${DESCRIPTION}', translation)])

        vr = bs.getEnvironment()['vrMode']
        d = bs.newNode('text',
                       attrs={
                           'vAttach': 'center',
                           'hAttach': 'center',
                           'hAlign': 'center',
                           'color': (1, 1, 1, 1),
                           'shadow': 1.0 if vr else 0.5,
                           'flatness': 1.0 if vr else 0.5,
                           'vrDepth': -30,
                           'position': (0, 80),
                           'scale': 1.2,
                           'maxWidth': 700,
                           'text': translation
                       })
        c = bs.newNode("combine",
                       owner=d,
                       attrs={
                           'input0': 1.0,
                           'input1': 1.0,
                           'input2': 1.0,
                           'size': 4
                       })
        c.connectAttr('output', d, 'color')
        keys = {500: 0, 1000: 1.0, 2500: 1.0, 4000: 0.0}
        bsUtils.animate(c, "input3", keys)
        bs.gameTimer(4000, d.delete)

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self.setupStandardTimeLimit(self.settings['Time Limit'])
        bs.gameTimer(5000, self.spawnZone)
        self._bots = bs.BotSet()
        bs.gameTimer(3000, bs.Call(self.addBot, 'left'))
        bs.gameTimer(3000, bs.Call(self.addBot, 'right'))
        if len(self.initialPlayerInfo) > 4:
            bs.gameTimer(5000, bs.Call(self.addBot, 'right'))
            bs.gameTimer(5000, bs.Call(self.addBot, 'left'))

        self._choseText = bs.newNode('text',
                                     attrs={
                                         'vAttach': 'bottom',
                                         'hAttach': 'left',
                                         'text': ' ',
                                         'opacity': 1.0,
                                         'maxWidth': 150,
                                         'hAlign': 'center',
                                         'vAlign': 'center',
                                         'shadow': 1.0,
                                         'flatness': 1.0,
                                         'color': (1, 1, 1),
                                         'scale': 1,
                                         'position': (50, 155)
                                     })

        if (isinstance(self.getSession(), bs.TeamsSession)
                and self.settings['Balance Total Lives']
                and len(self.teams[0].players) > 0
                and len(self.teams[1].players) > 0):
            if self._getTotalTeamLives(
                    self.teams[0]) < self._getTotalTeamLives(self.teams[1]):
                lesserTeam = self.teams[0]
                greaterTeam = self.teams[1]
            else:
                lesserTeam = self.teams[1]
                greaterTeam = self.teams[0]
            addIndex = 0
            while self._getTotalTeamLives(
                    lesserTeam) < self._getTotalTeamLives(greaterTeam):
                lesserTeam.players[addIndex].gameData['lives'] += 1
                addIndex = (addIndex + 1) % len(lesserTeam.players)

        self._updateIcons()
        bs.gameTimer(1000, self._update, repeat=True)

    def spawnZone(self):
        self.zonePos = (random.randrange(-10,
                                         10), 0.0, random.randrange(-5, 5))
        self.zone = bs.newNode('locator',
                               attrs={
                                   'shape': 'circle',
                                   'position': self.zonePos,
                                   'color': (1, 1, 0),
                                   'opacity': 0.5,
                                   'drawBeauty': True,
                                   'additive': False
                               })
        self.zoneLimit = bs.newNode('locator',
                                    attrs={
                                        'shape': 'circleOutline',
                                        'position': self.zonePos,
                                        'color': (1, 0.2, 0.2),
                                        'opacity': 0.8,
                                        'drawBeauty': True,
                                        'additive': False
                                    })
        bsUtils.animateArray(
            self.zone, 'size', 1, {
                0: [0],
                300: [self.getPlayersCount() * 0.85],
                350: [self.getPlayersCount() * 1]
            })
        bsUtils.animateArray(
            self.zoneLimit, 'size', 1, {
                0: [0],
                300: [self.getPlayersCount() * 1.2],
                350: [self.getPlayersCount() * 1.1]
            })
        bs.playSound(bs.getSound('laserReverse'))
        self.startTimer()
        self.moveZone()

    def deleteZone(self):
        scl = self.zone.size
        bsUtils.animateArray(self.zone, 'size', 1, {0: scl, 350: [0]})

        def a():
            self.zone.delete()
            self.zone = None
            self.zoneLimit.delete()
            self.zoneLimit = None
            bs.playSound(bs.getSound('shieldDown'))
            bs.gameTimer(1000, self.spawnZone)

        bs.gameTimer(350, a)

    def moveZone(self):
        if self.zonePos[0] > 0:
            x = random.randrange(0, 10)
        else:
            x = random.randrange(-10, 0)

        if self.zonePos[2] > 0:
            y = random.randrange(0, 5)
        else:
            y = random.randrange(-5, 0)

        newPos = (x, 0.0, y)
        bsUtils.animateArray(self.zone, 'position', 3, {
            0: self.zone.position,
            8000: newPos
        })
        bsUtils.animateArray(self.zoneLimit, 'position', 3, {
            0: self.zoneLimit.position,
            8000: newPos
        })

    def startTimer(self):
        count = self.getPlayersCount()
        self._timeRemaining = count if count > 2 else count * 2
        self._timerX = bs.Timer(1000, bs.WeakCall(self.tick), repeat=True)
        tint = bs.getSharedObject('globals').tint
        # bsUtils.animateArray(bs.getSharedObject('globals'),'tint',3,{0:tint,self._timeRemaining*1500:(1.0,0.5,0.5),self._timeRemaining*1550:tint})

    def stopTimer(self):
        self._time = None
        self._timerX = None

    def tick(self):
        self.check4Players()
        self._time = bs.NodeActor(
            bs.newNode('text',
                       attrs={
                           'vAttach': 'top',
                           'hAttach': 'center',
                           'text':
                           'Kill timer: ' + str(self._timeRemaining) + 's',
                           'opacity': 0.8,
                           'maxWidth': 100,
                           'hAlign': 'center',
                           'vAlign': 'center',
                           'shadow': 1.0,
                           'flatness': 1.0,
                           'color': (1, 1, 1),
                           'scale': 1.5,
                           'position': (0, -50)
                       }))
        self._timeRemaining -= 1
        bs.playSound(self._tickSound)

    def check4Players(self):
        if self._timeRemaining <= 0:
            self.stopTimer()
            bs.gameTimer(1500, self.deleteZone)
            for player in self.players:
                if not player.actor is None:
                    if player.actor.isAlive():
                        p1 = player.actor.node.position
                        p2 = self.zone.position
                        diff = (bs.Vector(p1[0] - p2[0], 0.0, p1[2] - p2[2]))
                        dist = (diff.length())
                        if dist > (self.getPlayersCount() * 0.7):
                            player.actor.handleMessage(bs.DieMessage())

    def getPlayersCount(self):
        count = 0
        for player in self.players:
            if not player.actor is None:
                if player.actor.isAlive():
                    count += 1
        return count

    def _getTotalTeamLives(self, team):
        return sum(player.gameData['lives'] for player in team.players)

    def onPlayerLeave(self, player):
        bs.TeamGameActivity.onPlayerLeave(self, player)
        player.gameData['icons'] = None
        bs.gameTimer(0, self._updateIcons)

    def _updateIcons(self):
        if isinstance(self.getSession(), bs.FreeForAllSession):
            count = len(self.teams)
            xOffs = 85
            x = xOffs * (count - 1) * -0.5
            for i, team in enumerate(self.teams):
                if len(team.players) == 1:
                    player = team.players[0]
                    for icon in player.gameData['icons']:
                        icon.setPositionAndScale((x, 30), 0.7)
                        icon.updateForLives()
                    x += xOffs
        else:
            for team in self.teams:
                if team.getID() == 0:
                    x = -50
                    xOffs = -85
                else:
                    x = 50
                    xOffs = 85
                for player in team.players:
                    for icon in player.gameData['icons']:
                        icon.setPositionAndScale((x, 30), 0.7)
                        icon.updateForLives()
                    x += xOffs

    def spawnPlayer(self, player):
        spaz = self.spawnPlayerSpaz(player)
        spaz.connectControlsToPlayer(enablePunch=False,
                                     enableBomb=False,
                                     enablePickUp=False)
        bs.gameTimer(300, bs.Call(self._printLives, player))
        for icon in player.gameData['icons']:
            icon.handlePlayerSpawned()

    def _printLives(self, player):
        if not player.exists() or not player.isAlive():
            return
        try:
            pos = player.actor.node.position
        except Exception, e:
            print 'EXC getting player pos in bsElim', e
            return
        bs.PopupText('x' + str(player.gameData['lives'] - 1),
                     color=(1, 1, 0, 1),
                     offset=(0, -0.8, 0),
                     randomOffset=0.0,
                     scale=1.8,
                     position=pos).autoRetain()

    def handleMessage(self, m):
        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self, m)
            player = m.spaz.getPlayer()

            player.gameData['lives'] -= 1
            if player.gameData['lives'] < 0:
                player.gameData['lives'] = 0

            for icon in player.gameData['icons']:
                icon.handlePlayerDied()

            if player.gameData['lives'] == 0:
                if self._getTotalTeamLives(player.getTeam()) == 0:
                    player.getTeam().gameData['survivalSeconds'] = (
                        bs.getGameTime() - self._startGameTime) / 1000
            else:
                self.respawnPlayer(player, self.settings['Respawn Times'])
        elif isinstance(m, bs.SpazBotDeathMessage):
            self._onSpazBotDied(m)
            bs.TeamGameActivity.handleMessage(self, m)
        else:
            bs.TeamGameActivity.handleMessage(self, m)

    def _onSpazBotDied(self, DeathMsg):
        bs.gameTimer(1000, bs.Call(self.addBot, DeathMsg.badGuy.node.position))

    def _onBotSpawn(self, spaz):
        spaz.updateCallback = self.moveBot
        spazType = type(spaz)
        spaz.walkSpeed = self._getBotSpeed(spazType)

    def addBot(self, pos=None):
        if pos == 'left':
            position = (-11, 0, random.randrange(-5, 5))
        elif pos == 'right':
            position = (11, 0, random.randrange(-5, 5))
        else:
            position = pos
        self._bots.spawnBot(self.getRandomBot(),
                            pos=position,
                            spawnTime=1000,
                            onSpawnCall=bs.Call(self._onBotSpawn))

    def moveBot(self, bot):
        p = bot.node.position
        speed = -bot.walkSpeed if (p[0] >= -11 and p[0] < 0) else bot.walkSpeed

        if (p[0] >= -11) and (p[0] <= 11):
            bot.node.moveLeftRight = speed
            bot.node.moveUpDown = 0.0
            bot.node.run = 0.0
            return True
        return False

    def getRandomBot(self):
        bots = [bs.BomberBotStatic, bs.ChickBotStatic]
        return (random.choice(bots))

    def _getBotSpeed(self, botType):
        if botType == bs.BomberBotStatic:
            return 0.48
        elif botType == bs.ChickBotStatic:
            return 0.73
        else:
            raise Exception('Invalid bot type to _getBotSpeed(): ' +
                            str(botType))

    def _update(self):
        if len(self._getLivingTeams()) < 2:
            self._roundEndTimer = bs.Timer(500, self.endGame)

    def _getLivingTeams(self):
        return [
            team for team in self.teams
            if len(team.players) > 0 and any(player.gameData['lives'] > 0
                                             for player in team.players)
        ]

    def endGame(self):
        if self.hasEnded():
            return
        self._sound = None
        self._logoEffect = None
        results = bs.TeamGameResults()
        self._vsText = None  # kill our 'vs' if its there
        for team in self.teams:
            results.setTeamScore(team, team.gameData['survivalSeconds'])
        self.end(results=results)
