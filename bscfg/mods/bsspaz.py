# -*- coding: utf-8 -*-
import bs
import bsBomb
import bsUtils
import random
import weakref
import bsInternal
import quakeBall
import mystats as ms
import some
import json
import bsSpaz
from bsSpaz import _PickupMessage, _PunchHitMessage, _CurseExplodeMessage, _BombDiedMessage
from bsSpaz import *
import bsPowerup
from bs import *
import math
import portalObjects
import DB_Manager as db
from thread import start_new_thread
#####STARTING MOD#####

bsSpaz.Spaz.curseBombCount = 0
bsSpaz.Spaz.forceBombCount = 0
bsSpaz.Spaz.triggerBombCount = 0
bsSpaz.Spaz.triggerBombs = []
bsSpaz.Spaz.trailblazerCount = 0
bsSpaz.Spaz.lastBackflipTime = 0
bsSpaz.Spaz.lastBetrayTime = 0
bsSpaz.Spaz.lastBombTime = 0
bsSpaz.Spaz.lastChangeTime = 0
bsSpaz.Spaz.autoaim = False
bsSpaz.Spaz.backflip = False
bsSpaz.Spaz.backflipProtection = False
bsSpaz.Spaz.backflipPresent = False
bsSpaz.Spaz._kick = False
bsSpaz.Spaz.invisible = False
bsSpaz.Spaz.footing = False
bsSpaz.Spaz.duringCatchphrase = False
bsSpaz.Spaz._kickedNodes = set()
#bsSpaz.Spaz.lastPowerup = []
bsSpaz.Spaz.enemyDrop = False


class _KickHitMessage(object):
    'Message saying an object was hit'
    pass


class _FootConnectMessage(object):
    'Player stands on ground'
    pass


class _FootDisconnectMessage(object):
    'Player stops touching the ground'
    pass


def SpazFactory__init__(self):
    """
    Instantiate a factory object.
    """

    self.impactSoundsMedium = (bs.getSound('impactMedium'),
                               bs.getSound('impactMedium2'))
    self.impactSoundsHard = (bs.getSound('impactHard'),
                             bs.getSound('impactHard2'),
                             bs.getSound('impactHard3'))
    self.impactSoundsHarder = (bs.getSound('bigImpact'),
                               bs.getSound('bigImpact2'))
    self.singlePlayerDeathSound = bs.getSound('playerDeath')
    self.punchSound = bs.getSound('punch01')

    self.punchSoundsStrong = (bs.getSound('punchStrong01'),
                              bs.getSound('punchStrong02'))

    self.punchSoundStronger = bs.getSound('superPunch')

    self.swishSound = bs.getSound('punchSwish')
    self.blockSound = bs.getSound('block')
    self.shatterSound = bs.getSound('shatter')
    self.splatterSound = bs.getSound('splatter')

    self.spazMaterial = bs.Material()
    self.rollerMaterial = bs.Material()
    self.punchMaterial = bs.Material()
    self.pickupMaterial = bs.Material()
    self.curseMaterial = bs.Material()
    self.kickMaterial = bs.Material()

    footingMaterial = bs.getSharedObject('footingMaterial')
    objectMaterial = bs.getSharedObject('objectMaterial')
    playerMaterial = bs.getSharedObject('playerMaterial')
    regionMaterial = bs.getSharedObject('regionMaterial')

    # send footing messages to spazzes so they know when they're on solid
    # ground.
    # eww this should really just be built into the spaz node
    self.kickMaterial.addActions(conditions=('theyAreDifferentNodeThanUs', ),
                                 actions=(('message', 'ourNode', 'atConnect',
                                           _KickHitMessage())))

    self.rollerMaterial.addActions(
        conditions=('theyHaveMaterial', footingMaterial),
        actions=(('message', 'ourNode', 'atConnect', 'footing', 1),
                 ('message', 'ourNode', 'atConnect', _FootConnectMessage()),
                 ('modifyPartCollision', 'friction',
                  1), ('message', 'ourNode', 'atDisconnect', 'footing',
                       -1), ('message', 'ourNode', 'atDisconnect',
                             _FootDisconnectMessage())))

    self.spazMaterial.addActions(
        conditions=('theyHaveMaterial', footingMaterial),
        actions=(('message', 'ourNode', 'atConnect', 'footing', 1),
                 ('message', 'ourNode', 'atConnect', _FootConnectMessage()),
                 ('modifyPartCollision', 'friction',
                  1), ('message', 'ourNode', 'atDisconnect', 'footing',
                       -1), ('message', 'ourNode', 'atDisconnect',
                             _FootDisconnectMessage())))
    # punches
    self.punchMaterial.addActions(conditions=('theyAreDifferentNodeThanUs', ),
                                  actions=(('modifyPartCollision', 'collide',
                                            True), ('modifyPartCollision',
                                                    'physical', False),
                                           ('message', 'ourNode', 'atConnect',
                                            _PunchHitMessage())))
    # pickups
    self.pickupMaterial.addActions(
        conditions=(('theyAreDifferentNodeThanUs', ), 'and',
                    ('theyHaveMaterial', objectMaterial)),
        actions=(('modifyPartCollision', 'collide',
                  True), ('modifyPartCollision', 'physical', False),
                 ('message', 'ourNode', 'atConnect', _PickupMessage())))
    # curse
    self.curseMaterial.addActions(conditions=(('theyAreDifferentNodeThanUs', ),
                                              'and', ('theyHaveMaterial',
                                                      playerMaterial)),
                                  actions=('message', 'ourNode', 'atConnect',
                                           _CurseExplodeMessage()))

    self.footImpactSounds = (bs.getSound('footImpact01'),
                             bs.getSound('footImpact02'),
                             bs.getSound('footImpact03'))

    self.footSkidSound = bs.getSound('skid01')
    self.footRollSound = bs.getSound('scamper01')

    self.rollerMaterial.addActions(
        conditions=('theyHaveMaterial', footingMaterial),
        actions=(('impactSound', self.footImpactSounds, 1,
                  0.2), ('skidSound', self.footSkidSound, 20, 0.3),
                 ('rollSound', self.footRollSound, 20, 3.0)))

    self.skidSound = bs.getSound('gravelSkid')

    self.spazMaterial.addActions(
        conditions=('theyHaveMaterial', footingMaterial),
        actions=(('impactSound', self.footImpactSounds, 20,
                  6), ('skidSound', self.skidSound, 2.0, 1),
                 ('rollSound', self.skidSound, 2.0, 1)))

    self.shieldUpSound = bs.getSound('shieldUp')
    self.shieldDownSound = bs.getSound('shieldDown')
    self.shieldHitSound = bs.getSound('shieldHit')

    # we dont want to collide with stuff we're initially overlapping
    # (unless its marked with a special region material)
    self.spazMaterial.addActions(
        conditions=((('weAreYoungerThan', 51), 'and',
                     ('theyAreDifferentNodeThanUs', )), 'and',
                    ('theyDontHaveMaterial', regionMaterial)),
        actions=(('modifyNodeCollision', 'collide', False)))

    self.spazMedia = {}

    # lets load some basic rules (allows them to be tweaked from the
    # master server)
    self.shieldDecayRate = bsInternal._getAccountMiscReadVal('rsdr', 10.0)
    self.punchCooldown = bsInternal._getAccountMiscReadVal('rpc', 400)
    self.punchCooldownGloves = \
        bsInternal._getAccountMiscReadVal('rpcg', 300)
    self.punchPowerScale = bsInternal._getAccountMiscReadVal('rpp', 1.2)
    self.punchPowerScaleGloves = \
        bsInternal._getAccountMiscReadVal('rppg', 1.4)
    self.maxShieldSpilloverDamage = \
        bsInternal._getAccountMiscReadVal('rsms', 500)


def onPunchPress(self):
    """
    Called to 'press punch' on this spaz;
    used for player or AI connections.
    """
    if not self.node.exists() or self.frozen or self.node.knockout > 0.0:
        return
    if self.punchCallback is not None:
        self.punchCallback(self)
        if self.trailblazerCount > 1:
            quakeBall.QuakeBallFactory().give(self)
        if self.trailblazerCount > 0:
            self.setTrailblazerCount(self.trailblazerCount - 1)
    t = bs.getGameTime()
    self._punchedNodes = set()  # reset this..
    if t - self.lastPunchTime > self._punchCooldown:
        self.lastPunchTime = t
        self.node.punchPressed = True
        if not self.node.holdNode.exists():
            bs.gameTimer(
                100,
                bs.WeakCall(self._safePlaySound,
                            self.getFactory().swishSound, 0.8))
        else:
            self.lastPunchTime = 0


def onJumpPress(self):
    """
    Called to 'press jump' on this spaz;
    used by player or AI connections.
    """

    if not self.node.exists():
        return
    t = bs.getGameTime()
    if t - self.lastJumpTime >= self._jumpCooldown:
        self.node.jumpPressed = True
        self.lastJumpTime = t
    if self.backflip and (self.node.punchPressed or
                          (bs.getGameTime() - self.lastPunchTime) < 300) and (
                              bs.getGameTime() - self.lastBackflipTime) > 1000:
        if not self._kick:
            factory = self.getFactory()
            self._kick = True
            # add kick material
            for attr in ['materials', 'rollerMaterials']:
                materials = getattr(self.node, attr)
                if not factory.kickMaterial in materials:
                    setattr(self.node, attr,
                            materials + (factory.kickMaterial, ))
        self.node.handleMessage("impulse", self.node.position[0],
                                self.node.position[1] - 3,
                                self.node.position[2], self.node.velocity[0],
                                self.node.velocity[1], self.node.velocity[2],
                                50 * self.node.run, 10 * self.node.run, 0, 0,
                                self.node.velocity[0], self.node.velocity[1],
                                self.node.velocity[2])
        self.node.handleMessage("impulse", self.node.position[0],
                                self.node.position[1] - 5,
                                self.node.position[2], self.node.velocity[0],
                                self.node.velocity[1], self.node.velocity[2],
                                50 * self.node.run, 20 * self.node.run, 0, 0,
                                self.node.velocity[0], self.node.velocity[1],
                                self.node.velocity[2])
        self.node.handleMessage("impulse", self.node.position[0],
                                self.node.position[1] - 5,
                                self.node.position[2], 0, 10, 0, 50, 20, 0, 0,
                                0, 10, 0)
        bs.emitBGDynamics(position=(self.node.position[0],
                                    self.node.position[1] - 0.2,
                                    self.node.position[2]),
                          velocity=(self.node.velocity[0] * 5,
                                    self.node.velocity[1] * 2,
                                    self.node.velocity[2]),
                          count=random.randrange(12, 20),
                          scale=0.35,
                          spread=0.31,
                          chunkType='spark')
        bsUtils.PopupText("Haiyaa!",
                          color=(0, 1, 1),
                          scale=1.3,
                          position=self.node.position).autoRetain()
        self.lastBackflipTime = bs.getGameTime()
        self._kickedNodes = set()

    def backflip_off():
        if self.node.exists():
            if self._kick:
                self._kick = False
                # remove kick material
                factory = self.getFactory()
                for attr in ['materials', 'rollerMaterials']:
                    materials = getattr(self.node, attr)
                    if factory.kickMaterial in materials:
                        setattr(
                            self.node, attr,
                            tuple(m for m in materials
                                  if m != factory.kickMaterial))

    bs.gameTimer(500, backflip_off)


def onJumpRelease(self):
    """
    Called to 'release jump' on this spaz;
    used by player or AI connections.
    """
    if not self.node.exists():
        return
    # power = (bs.getGameTime() - self.lastJumpTime)/1000*150
    # msg = self.node
    # self.node.handleMessage("impulse", msg.position[0], msg.position[1]+0.5, msg.position[2],
    #                     0, 10, 0,
    #                     power,5,0,0,
    #                     0, 10, 0)
    self.node.jumpPressed = False
    if self.node.exists():
        if self._kick:
            self._kick = False
            # remove kick material
            factory = self.getFactory()
            for attr in ['materials', 'rollerMaterials']:
                materials = getattr(self.node, attr)
                if factory.kickMaterial in materials:
                    setattr(
                        self.node, attr,
                        tuple(m for m in materials
                              if m != factory.kickMaterial))


def onPickUpPress(self):
    """
    Called to 'press pick-up' on this spaz;
    used by player or AI connections.
    """
    if not self.node.exists():
        return
    if self.triggerBombs:
        for i in self.triggerBombs:
            if i.exists():
                p = self.node.position
                p2 = i.node.position
                diff = (bs.Vector(p[0] - p2[0], 0.0, p[2] - p2[2]))
                dist = (diff.length())
                if self.node.holdNode != i.node and dist > 1:
                    i.handleMessage(bsBomb.ExplodeMessage())
            else:
                i.handleMessage(bsBomb.ExplodeMessage())
    self.node.pickUpPressed = True


def onPickUpRelease(self):
    """
    Called to 'release pick-up' on this spaz;
    used by player or AI connections.
    """
    if not self.node.exists():
        return
    self.node.pickUpPressed = False


def _onHoldPositionPress(self):
    """
    Called to 'press hold-position' on this spaz;
    used for player or AI connections.
    """
    if not self.node.exists():
        return
    self.node.holdPositionPressed = True


def _onHoldPositionRelease(self):
    """
    Called to 'release hold-position' on this spaz;
    used for player or AI connections.
    """
    if not self.node.exists():
        return
    self.node.holdPositionPressed = False


def onPunchRelease(self):
    """
    Called to 'release punch' on this spaz;
    used for player or AI connections.
    """
    if not self.node.exists():
        return
    self.node.punchPressed = False


def onBombPress(self):
    """
    Called to 'press bomb' on this spaz;
    used for player or AI connections.
    """
    if not self.node.exists():
        return
    if self._dead or self.frozen:
        return
    if self.node.knockout > 0.0:
        return
    self.lastBombTime = bs.getGameTime()
    self.node.bombPressed = True
    if not self.node.holdNode.exists():
        self.dropBomb()

    def trigger_backflip():
        if self.node.exists():
            if self.node.bombPressed:
                self.backflip = not self.backflip
                bsUtils.PopupText(
                    'Backflip: ON' if self.backflip else 'Backflip: OFF',
                    color=(1, 1, 1),
                    scale=1.3,
                    position=self.node.position).autoRetain()

    if self.backflipPresent:
        self.triggertimer = bs.Timer(300, trigger_backflip)


def onBombRelease(self):
    """
    Called to 'release bomb' on this spaz;
    used for player or AI connections.
    """
    if not self.node.exists():
        return
    self.node.bombPressed = False


def onRun(self, value):
    """
    Called to 'press run' on this spaz;
    used for player or AI connections.
    """
    if not self.node.exists():
        return
    self.node.run = value


def onFlyPress(self):
    """
    Called to 'press fly' on this spaz;
    used for player or AI connections.
    """
    if not self.node.exists():
        return
    self.node.flyPressed = True


def onFlyRelease(self):
    """
    Called to 'release fly' on this spaz;
    used for player or AI connections.
    """
    if not self.node.exists():
        return
    self.node.flyPressed = False


def onMove(self, x, y):
    """
    Called to set the joystick amount for this spaz;
    used for player or AI connections.
    """
    if not self.node.exists():
        return
    self.node.handleMessage("move", x, y)


def onMoveUpDown(self, value):
    """
    Called to set the up/down joystick amount on this spaz;
    used for player or AI connections.
    value will be between -32768 to 32767
    WARNING: deprecated; use onMove instead.
    """
    if not self.node.exists():
        return
    self.lastChangeTime = bs.getRealTime()
    self.node.moveUpDown = value


def onMoveLeftRight(self, value):
    """
    Called to set the left/right joystick amount on this spaz;
    used for player or AI connections.
    value will be between -32768 to 32767
    WARNING: deprecated; use onMove instead.
    """
    if not self.node.exists():
        return
    self.lastChangeTime = bs.getRealTime()
    self.node.moveLeftRight = value


def setInvisibility(self):
    light = bs.newNode('light',
                       attrs={
                           'position': (self.node.position),
                           'color': self.node.color,
                           'volumeIntensityScale': 1.0,
                           'radius': 0.1
                       })
    bsUtils.animate(light, "intensity", {0: 0, 50: 5, 500: 0})
    bs.playSound(bs.getSound('shieldDown'))
    self.node.connectAttr('positionCenter', light, 'position')

    self._name = self.node.name
    self._style = self.node.style
    self._head = self.node.headModel
    self._torso = self.node.torsoModel
    self._pelvis = self.node.pelvisModel
    self._upperArm = self.node.upperArmModel
    self._foreArm = self.node.foreArmModel
    self._hand = self.node.handModel
    self._upperLeg = self.node.upperLegModel
    self._lowerLeg = self.node.lowerLegModel
    self._toes = self.node.toesModel
    try:
        self._effectscale = self.effect._Text.scale
    except:
        pass
    self._hpscale = self.hp._Text.scale

    self.node.name = ' '
    try:
        self.companion.handleMessage(bs.DieMessage())
    except Exception as e:
        pass
    try:
        self.effect._Text.text = ''
    except:
        pass
    self.node.style = 'agent'
    self.invisible = True
    self.node.headModel = None
    self.node.torsoModel = None
    self.node.pelvisModel = None
    self.node.upperArmModel = None
    self.node.foreArmModel = None
    self.node.handModel = None
    self.node.upperLegModel = None
    self.node.lowerLegModel = None
    self.node.toesModel = None
    self.effect._Text.scale = 0
    self.hp._Text.scale = 0


def handleMessage(self, m):
    self._handleMessageSanityCheck()

    if isinstance(m, bs.PickedUpMessage):
        self.node.handleMessage("hurtSound")
        self.node.handleMessage("pickedUp")
        # this counts as a hit
        self._numTimesHit += 1

    elif isinstance(m, bs.ShouldShatterMessage):
        # eww; seems we have to do this in a timer or it wont work right
        # (since we're getting called from within update() perhaps?..)
        bs.gameTimer(1, bs.WeakCall(self.shatter))

    elif isinstance(m, bs.ImpactDamageMessage):
        # eww; seems we have to do this in a timer or it wont work right
        # (since we're getting called from within update() perhaps?..)
        bs.gameTimer(1, bs.WeakCall(self._hitSelf, m.intensity))

    elif isinstance(m, bs.PowerupMessage):
        #if not m.powerupType in self.lastPowerup:
        #self.lastPowerup.append(m.powerupType)
        #def removefromlist(player,pt):
        #try:
        #player.lastPowerup.remove(pt)
        #except:
        #pass
        #bs.gameTimer(60000,bs.Call(removefromlist,self,m.powerupType))
        if self._dead:
            return True
        if self.pickUpPowerupCallback is not None:
            self.pickUpPowerupCallback(self)

        if some.modded_powerups: bsUtils.PopupText(m.powerupType.upper() + "!",
                          color=(0.2, 1, 0.2),
                          scale=1.2,
                          position=self.node.position).autoRetain()
        if (m.powerupType == 'tripleBombs'):
            tex = bs.Powerup.getFactory().texBomb
            self._flashBillboard(tex)
            self.setBombCount(3)
            if self.powerupsExpire:
                self.node.miniBillboard1Texture = tex
                t = bs.getGameTime()
                self.node.miniBillboard1StartTime = t
                self.node.miniBillboard1EndTime = t + gPowerupWearOffTime
                self._multiBombWearOffFlashTimer = bs.Timer(
                    gPowerupWearOffTime - 2000,
                    bs.WeakCall(self._multiBombWearOffFlash))
                self._multiBombWearOffTimer = bs.Timer(
                    gPowerupWearOffTime, bs.WeakCall(self._multiBombWearOff))
        elif m.powerupType == 'landMines':
            self.setLandMineCount(min(self.landMineCount + 3, 3))
        elif m.powerupType == 'triggerBombs':
            bsUtils.PopupText("Press Pick-Up to explode!",
                              color=(0, 1, 1),
                              scale=1.3,
                              position=(self.node.position[0],
                                        self.node.position[1] - 0.5,
                                        self.node.position[2])).autoRetain()
            self.setTriggerBombCount(min(self.triggerBombCount + 5, 5))
        elif m.powerupType == 'clusterBombs':
            self.bombType = 'cluster'
            tex = self._getBombTypeTex()
            self._flashBillboard(tex)
            if self.powerupsExpire:
                self.node.miniBillboard2Texture = tex
                t = bs.getGameTime()
                self.node.miniBillboard2StartTime = t
                self.node.miniBillboard2EndTime = t + gPowerupWearOffTime
                self._bombWearOffFlashTimer = bs.Timer(
                    gPowerupWearOffTime - 2000,
                    bs.WeakCall(self._bombWearOffFlash))
                self._bombWearOffTimer = bs.Timer(
                    gPowerupWearOffTime, bs.WeakCall(self._bombWearOff))

        elif m.powerupType == 'impactBombs':
            self.bombType = 'impact'
            tex = self._getBombTypeTex()
            self._flashBillboard(tex)
            if self.powerupsExpire:
                self.node.miniBillboard2Texture = tex
                t = bs.getGameTime()
                self.node.miniBillboard2StartTime = t
                self.node.miniBillboard2EndTime = t + gPowerupWearOffTime
                self._bombWearOffFlashTimer = bs.Timer(
                    gPowerupWearOffTime - 2000,
                    bs.WeakCall(self._bombWearOffFlash))
                self._bombWearOffTimer = bs.Timer(
                    gPowerupWearOffTime, bs.WeakCall(self._bombWearOff))

        elif m.powerupType == 'heatSeeker':
            self.setForceBombCount(min(self.forceBombCount + 1, 2))
        elif m.powerupType == 'autoaim':
            tex = bs.Powerup.getFactory().texAim
            self._flashBillboard(tex)
            self.autoaim = True
            self.bombType = 'normal'
            if self.powerupsExpire:
                self.node.miniBillboard1Texture = tex
                t = bs.getGameTime()
                self.node.miniBillboard1StartTime = t
                self.node.miniBillboard1EndTime = t + gPowerupWearOffTime
                self._multiBombWearOffFlashTimer = bs.Timer(
                    gPowerupWearOffTime - 2000,
                    bs.WeakCall(self._multiBombWearOffFlash))

                def off():
                    self.autoaim = False

                self._multiBombWearOffTimer = bs.Timer(gPowerupWearOffTime,
                                                       off)
        elif m.powerupType == 'droneStrike':

            class zone(object):
                def __init__(self, player):
                    self.pos = player.actor.node.position
                    self.zone = bs.newNode('light',
                                           owner=player.actor.node,
                                           attrs={
                                               'position': self.pos,
                                               'color': (0.5, 0.5, 1),
                                               'intensity': 10,
                                               'heightAttenuated': True
                                           })
                    bsUtils.animate(self.zone, 'radius', {0: 0, 300: 0.05})
                    bsUtils.animate(self.zone, 'radius', {1700: 0.05, 2000: 0})
                    bs.gameTimer(2000, self.zone.delete)

            # def strike():
            #     activity = bsInternal._getForegroundHostActivity()
            #     for player in activity.players:
            #         if player.actor is not None and player.actor.isAlive() and player.getTeam() != self.sourcePlayer.getTeam():
            #             blast = Blast(position=player.actor.node.position,velocity=player.actor.node.velocity,
            #                                             blastRadius=3,blastType='landmine',sourcePlayer=self.sourcePlayer).autoRetain()
            #             player.actor.node.shattered = 3
            #     bs.shakeCamera(5)
            import portalObjects
            activity = bsInternal._getForegroundHostActivity()
            for player in activity.players:
                if player.actor is not None and player.actor.isAlive(
                ) and player.getTeam() != self.sourcePlayer.getTeam():
                    zone(player)
                    portalObjects.Artillery(target=player.actor.node,
                                            sourcePlayer=self.sourcePlayer)

            bs.screenMessage('%s called in a drone strike!' %
                             self.sourcePlayer.getName(),
                             color=(1, 1, 0))
            # bs.gameTimer(500,strike)

        elif m.powerupType == 'bubblePower':

            class zone(object):
                def __init__(self, player):
                    self.pos = player.actor.node.position
                    self.node = player.actor.node
                    self.up = 1
                    self.zone = bs.newNode('light',
                                           owner=player.actor.node,
                                           attrs={
                                               'position': self.pos,
                                               'color': (1, 0, 0),
                                               'intensity': 10,
                                               'heightAttenuated': True
                                           })
                    self.shield = bs.newNode('shield',
                                             owner=self.node,
                                             attrs={
                                                 'color': (1, 0, 0),
                                                 'radius': 1.3
                                             })
                    self.node.connectAttr('positionCenter', self.shield,
                                          'position')
                    self.node.connectAttr('positionCenter', self.zone,
                                          'position')
                    bsUtils.animate(self.zone, 'radius', {0: 0, 300: 0.05})
                    bsUtils.animate(self.zone, 'radius', {700: 0.05, 1000: 0})
                    self.fly()
                    bs.gameTimer(1000, self.zone.delete)
                    bs.gameTimer(1000, self.shield.delete)
                    bs.gameTimer(1000, self.off)

                def fly(self):
                    if self.node.getDelegate().isAlive() and self.up == 1:
                        self.node.handleMessage("impulse",
                                                self.node.position[0],
                                                self.node.position[1] + .5,
                                                self.node.position[2], 0, 5, 0,
                                                3, 10, 0, 0, 0, 5, 0)
                        bs.gameTimer(35, self.fly)
                    if self.up == 0:
                        self.up = -1
                        self.node.handleMessage("impulse",
                                                self.node.position[0],
                                                self.node.position[1] + .5,
                                                self.node.position[2], 0, -50,
                                                0, 3, 10, 0, 0, 0, -50, 0)

                def off(self):
                    self.up = 0

            # def strike():
            #     activity = bsInternal._getForegroundHostActivity()
            #     for player in activity.players:
            #         if player.actor is not None and player.actor.isAlive() and player.getTeam() != self.sourcePlayer.getTeam():
            #             blast = Blast(position=player.actor.node.position,velocity=player.actor.node.velocity,
            #                                             blastRadius=3,blastType='landmine',sourcePlayer=self.sourcePlayer).autoRetain()
            #             player.actor.node.shattered = 3
            #     bs.shakeCamera(5)
            import portalObjects
            activity = bsInternal._getForegroundHostActivity()
            for player in activity.players:
                if player.actor is not None and player.actor.isAlive(
                ) and player.getTeam() != self.sourcePlayer.getTeam():
                    zone(player)

            bs.screenMessage('%s used his hidden powers!' %
                             self.sourcePlayer.getName(),
                             color=(1, 1, 0))
            # bs.gameTimer(500,strike)

        elif m.powerupType == 'trailblazer':
            quakeBall.QuakeBallFactory().give(self)
            self.setTrailblazerCount(min(self.trailblazerCount + 3, 3))
        elif m.powerupType == 'portal':
            import portalObjects
            portpos = self.node.position
            bs.playSound(bs.getSound('shieldUp'))
            defs1 = random.choice(
                bs.getActivity().getMap().getDefPoints('powerupSpawn'))[0:3]
            defs2 = random.choice(
                bs.getActivity().getMap().getDefPoints('spawn'))[0:3]
            defs3 = random.choice(
                bs.getActivity().getMap().getDefPoints('ffaSpawn'))[0:3]
            defs = random.choice([defs1, defs2, defs3])
            port = portalObjects.Portal(
                position1=(portpos[0] + random.uniform(2, -2), portpos[1],
                           portpos[2] + random.uniform(2, -2)),
                position2=(defs[0], defs[1] + 0.5, defs[2]),
                color=(random.random(), random.random(), random.random()))

        elif m.powerupType == 'curseBomb':
            self.setcurseBombCount(self.curseBombCount + 1)

        elif m.powerupType == 'invisible':
            tex = bs.Powerup.getFactory().texRainbow
            self._flashBillboard(tex)
            try:
                self.setInvisibility()
            except:
                pass
            self._isInvisible = True
            if self.powerupsExpire:
                self.node.miniBillboard3Texture = tex
                t = bs.getGameTime()
                self.node.miniBillboard3StartTime = t
                self.node.miniBillboard3EndTime = t + gPowerupWearOffTime
                self._invisibilityWearOffFlashTimer = bs.Timer(
                    gPowerupWearOffTime - 2000,
                    bs.WeakCall(self._invisibilityWearOffFlash))
                self._invisibilityWearOffTimer = bs.Timer(
                    gPowerupWearOffTime,
                    bs.WeakCall(self._invisibilityWearOff))

        elif m.powerupType == 'stickyBombs':
            self.bombType = 'sticky'
            tex = self._getBombTypeTex()
            self._flashBillboard(tex)
            if self.powerupsExpire:
                self.node.miniBillboard2Texture = tex
                t = bs.getGameTime()
                self.node.miniBillboard2StartTime = t
                self.node.miniBillboard2EndTime = t + gPowerupWearOffTime
                self._bombWearOffFlashTimer = bs.Timer(
                    gPowerupWearOffTime - 2000,
                    bs.WeakCall(self._bombWearOffFlash))
                self._bombWearOffTimer = bs.Timer(
                    gPowerupWearOffTime, bs.WeakCall(self._bombWearOff))
        elif m.powerupType == 'punch':
            self._hasBoxingGloves = True
            tex = bs.Powerup.getFactory().texPunch
            self._flashBillboard(tex)
            self.equipBoxingGloves()
            if self.powerupsExpire:
                self.node.boxingGlovesFlashing = 0
                self.node.miniBillboard3Texture = tex
                t = bs.getGameTime()
                self.node.miniBillboard3StartTime = t
                self.node.miniBillboard3EndTime = t + gPowerupWearOffTime
                self._boxingGlovesWearOffFlashTimer = bs.Timer(
                    gPowerupWearOffTime - 2000,
                    bs.WeakCall(self._glovesWearOffFlash))
                self._boxingGlovesWearOffTimer = bs.Timer(
                    gPowerupWearOffTime, bs.WeakCall(self._glovesWearOff))
        elif m.powerupType == 'shield':
            factory = self.getFactory()
            # let's allow powerup-equipped shields to lose hp over time
            self.equipShields(
                decay=True if factory.shieldDecayRate > 0 else False)
        elif m.powerupType == 'curse':
            self.curse()
        elif (m.powerupType == 'iceBombs'):
            self.bombType = 'ice'
            tex = self._getBombTypeTex()
            self._flashBillboard(tex)
            if self.powerupsExpire:
                self.node.miniBillboard2Texture = tex
                t = bs.getGameTime()
                self.node.miniBillboard2StartTime = t
                self.node.miniBillboard2EndTime = t + gPowerupWearOffTime
                self._bombWearOffFlashTimer = bs.Timer(
                    gPowerupWearOffTime - 2000,
                    bs.WeakCall(self._bombWearOffFlash))
                self._bombWearOffTimer = bs.Timer(
                    gPowerupWearOffTime, bs.WeakCall(self._bombWearOff))
        elif (m.powerupType == 'health'):
            if self._cursed:
                self._cursed = False
                # remove cursed material
                factory = self.getFactory()
                for attr in ['materials', 'rollerMaterials']:
                    materials = getattr(self.node, attr)
                    if factory.curseMaterial in materials:
                        setattr(
                            self.node, attr,
                            tuple(m for m in materials
                                  if m != factory.curseMaterial))
                self.node.curseDeathTime = 0
            self.hitPoints = self.hitPointsMax
            self._flashBillboard(bs.Powerup.getFactory().texHealth)
            self.node.hurt = 0
            self._lastHitTime = None
            self._numTimesHit = 0

        self.node.handleMessage("flash")
        if m.sourceNode.exists():
            m.sourceNode.handleMessage(bs.PowerupAcceptMessage())
        return True

    elif isinstance(m, bs.FreezeMessage):
        if not self.node.exists():
            return
        if self.node.invincible == True:
            bs.playSound(self.getFactory().blockSound,
                         1.0,
                         position=self.node.position)
            return
        if self.shield is not None:
            return
        if not self.frozen:
            self.frozen = True
            self.node.frozen = 1
            bs.gameTimer(5000, bs.WeakCall(self.handleMessage,
                                           bs.ThawMessage()))
            # instantly shatter if we're already dead (otherwise its hard to tell we're dead)
            if self.hitPoints <= 0:
                self.shatter()

    elif isinstance(m, bs.ThawMessage):
        if self.frozen and not self.shattered and self.node.exists():
            self.frozen = False
            self.node.frozen = 0

    elif isinstance(m, _KickHitMessage):
        node = bs.getCollisionInfo("opposingNode")

        # only allow one hit per node per punch
        if (node is not None and node.exists()
                and not node in self._kickedNodes and self.onJumpPress
                and self.onPunchPress):

            kickMomentumAngular = (
                (self.node.punchMomentumAngular or self.node.run) * 0.77)
            kickPower = (self.node.punchPower or self.node.run) * 0.77

            # ok here's the deal:  we pass along our base velocity for use
            # in the impulse damage calculations since that is a more
            # predictable value than our fist velocity, which is rather
            # erratic. ...however we want to actually apply force in the
            # direction our fist is moving so it looks better.. so we still
            # pass that along as a direction ..perhaps a time-averaged
            # fist-velocity would work too?.. should try that.

            # if its something besides another spaz, just do a muffled punch
            # sound
            if node.getNodeType() != 'spaz':
                sounds = self.getFactory().impactSoundsMedium
                sound = sounds[random.randrange(len(sounds))]
                bs.playSound(sound, 1.0, position=self.node.position)
            else:
                if node.getDelegate().backflipProtection: self.catchphrase('Why can\'t I hit you!?');return
                self.catchphrase()

            t = (self.node.position[0], self.node.position[1],
                 self.node.position[2])
            kickDir = (self.node.velocity[0], self.node.velocity[1] + 5,
                       self.node.velocity[2])
            v = self.node.velocity

            self._kickedNodes.add(node)
            node.handleMessage(
                bs.HitMessage(pos=t,
                              velocity=v,
                              magnitude=kickPower * kickMomentumAngular *
                              100.0,
                              velocityMagnitude=kickPower * 60,
                              radius=-1000,
                              srcNode=self.node,
                              sourcePlayer=self.sourcePlayer,
                              forceDirection=kickDir,
                              hitType='kick'))
            node.handleMessage(
                "impulse", self.node.position[0], self.node.position[1] - 0.2,
                self.node.position[2], self.node.velocity[0] * 5,
                self.node.velocity[1] * 2, self.node.velocity[2],
                kickPower * kickMomentumAngular * 110, kickPower * 60, 0, 0,
                self.node.velocity[0] * 5, self.node.velocity[1] * 2,
                self.node.velocity[2])
            bs.emitBGDynamics(position=(self.node.position[0],
                                        self.node.position[1] - 0.2,
                                        self.node.position[2]),
                              velocity=(self.node.velocity[0] * 5,
                                        self.node.velocity[1] * 2,
                                        self.node.velocity[2]),
                              count=random.randrange(12, 20),
                              scale=0.35,
                              spread=0.31,
                              chunkType='spark')

    elif isinstance(m, bs.HitMessage):
        if not self.node.exists():
            return
        if self.node.invincible == True:
            bs.playSound(self.getFactory().blockSound,
                         1.0,
                         position=self.node.position)
            return True

        # if we were recently hit, don't count this as another
        # (so punch flurries and bomb pileups essentially count as 1 hit)
        gameTime = bs.getGameTime()
        if self._lastHitTime is None or gameTime - self._lastHitTime > 1000:
            self._numTimesHit += 1
            self._lastHitTime = gameTime

        mag = m.magnitude * self._impactScale
        velocityMag = m.velocityMagnitude * self._impactScale

        damageScale = 0.22

        # if they've got a shield, deliver it to that instead..
        if self.shield is not None:

            if m.flatDamage:
                damage = m.flatDamage * self._impactScale
            else:
                # hit our spaz with an impulse but tell it to only return theoretical damage; not apply the impulse..
                self.node.handleMessage("impulse", m.pos[0], m.pos[1],
                                        m.pos[2], m.velocity[0], m.velocity[1],
                                        m.velocity[2], mag, velocityMag,
                                        m.radius, 1, m.forceDirection[0],
                                        m.forceDirection[1],
                                        m.forceDirection[2])
                damage = damageScale * self.node.damage

            self.shieldHitPoints -= damage

            self.shield.hurt = 1.0 - \
                float(self.shieldHitPoints)/self.shieldHitPointsMax
            # its a cleaner event if a hit just kills the shield without damaging the player..
            # however, massive damage events should still be able to damage the player..
            # this hopefully gives us a happy medium.
            # maxSpillover = 500
            maxSpillover = self.getFactory().maxShieldSpilloverDamage
            if self.shieldHitPoints <= 0:
                # fixme - transition out perhaps?..
                self.shield.delete()
                self.shield = None
                bs.playSound(self.getFactory().shieldDownSound,
                             1.0,
                             position=self.node.position)
                # emit some cool lookin sparks when the shield dies
                t = self.node.position
                bs.emitBGDynamics(position=(t[0], t[1] + 0.9, t[2]),
                                  velocity=self.node.velocity,
                                  count=random.randrange(20, 30),
                                  scale=1.0,
                                  spread=0.6,
                                  chunkType='spark')

            else:
                bs.playSound(self.getFactory().shieldHitSound,
                             0.5,
                             position=self.node.position)

            # emit some cool lookin sparks on shield hit
            bs.emitBGDynamics(position=m.pos,
                              velocity=(m.forceDirection[0] * 1.0,
                                        m.forceDirection[1] * 1.0,
                                        m.forceDirection[2] * 1.0),
                              count=min(30, 5 + int(damage * 0.005)),
                              scale=0.5,
                              spread=0.3,
                              chunkType='spark')

            # if they passed our spillover threshold, pass damage along to spaz
            if self.shieldHitPoints <= -maxSpillover:
                leftoverDamage = -maxSpillover - self.shieldHitPoints
                shieldLeftoverRatio = leftoverDamage / damage

                # scale down the magnitudes applied to spaz accordingly..
                mag *= shieldLeftoverRatio
                velocityMag *= shieldLeftoverRatio
            else:
                return True  # good job shield!
        else:
            shieldLeftoverRatio = 1.0

        if m.flatDamage:
            damage = m.flatDamage * self._impactScale * shieldLeftoverRatio
        else:
            # hit it with an impulse and get the resulting damage
            self.node.handleMessage("impulse", m.pos[0], m.pos[1], m.pos[2],
                                    m.velocity[0], m.velocity[1],
                                    m.velocity[2], mag, velocityMag, m.radius,
                                    0, m.forceDirection[0],
                                    m.forceDirection[1], m.forceDirection[2])

            damage = damageScale * self.node.damage
        self.node.handleMessage("hurtSound")

        bs.emitBGDynamics(position=(self.node.position[0],
                                    self.node.position[1] - 0.2,
                                    self.node.position[2]),
                          velocity=(self.node.velocity[0] * 5,
                                    self.node.velocity[1] * 2,
                                    self.node.velocity[2]),
                          count=4 * int(damage / 100),
                          scale=0.4,
                          spread=0.31,
                          chunkType='spark')  # Extra Sparks For Da Lulz

        # play punch impact sound based on damage if it was a punch
        if m.hitType == 'punch':

            self.onPunched(damage)

            if damage >= 1000:
                ab = bs.getCollisionInfo("sourceNode")
                if hasattr(ab, 'sourcePlayer'):
                    import portalObjects
                    try:
                        bs.screenMessage(bs.Lstr(
                            value=
                            '${PLAYER} Started A BlackHole With That Punch!!',
                            subs=[('${PLAYER}', ab.sourcePlayer.getName(True))
                                  ]),
                                         color=(1, 1, 0))
                    except:
                        pass
                    bh = portalObjects.BlackHole(position=self.node.position,
                                                 owner=self.node)
                    bsUtils.PopupText(
                        "FATALITY!!!",
                        color=(1, 0, 0),
                        scale=2.0,
                        position=self.node.position).autoRetain()
                    self.lightningBolt(position=self.node.position, radius=3)
                    # if bs.getSharedObject('globals').slowMotion == False:
                    #   def slowMo():
                    #      bs.getSharedObject('globals').slowMotion = bs.getSharedObject('globals').slowMotion == False
                    # slowMo()
                # bs.gameTimer(600,bs.Call(slowMo))
                else:
                    pass

            elif damage >= 600 and damage < 1000:
                # bsUtils.PopupText("AWESOME!!",color=(0,1,0.3),scale=1.6,position=self.node.position).autoRetain()
                pass

            elif damage > 530 and damage < 600:
                # bsUtils.PopupText("COOL!",color=(1,0,0),scale=1.6,position=self.node.position).autoRetain()
                pass

            if m.hitSubType == 'superPunch':
                bs.playSound(self.getFactory().punchSoundStronger,
                             1.0,
                             position=self.node.position)

            if damage > 500:
                sounds = self.getFactory().punchSoundsStrong
                sound = sounds[random.randrange(len(sounds))]
            else:
                sound = self.getFactory().punchSound
            bs.playSound(sound, 1.0, position=self.node.position)

            # throw up some chunks
            bs.emitBGDynamics(position=m.pos,
                              velocity=(m.forceDirection[0] * 0.5,
                                        m.forceDirection[1] * 0.5,
                                        m.forceDirection[2] * 0.5),
                              count=min(10, 3 + int(damage * 0.0025)),
                              scale=0.3,
                              spread=0.03)

            bs.emitBGDynamics(position=m.pos,
                              chunkType='sweat',
                              velocity=(m.forceDirection[0] * 1.3,
                                        m.forceDirection[1] * 1.3 + 5.0,
                                        m.forceDirection[2] * 1.3),
                              count=min(30, 1 + int(damage * 0.04)),
                              scale=0.9,
                              spread=0.28)
            # momentary flash
            hurtiness = damage * 0.003
            punchPos = (m.pos[0] + m.forceDirection[0] * 0.02,
                        m.pos[1] + m.forceDirection[1] * 0.02,
                        m.pos[2] + m.forceDirection[2] * 0.02)
            flashColor = (1.0, 0.2, 0.2)
            light = bs.newNode("light",
                               attrs={
                                   'position': punchPos,
                                   'radius': 0.52 + hurtiness * 0.12,
                                   'intensity': 0.3 * (1.0 + 1.0 * hurtiness),
                                   'heightAttenuated': False,
                                   'color': flashColor
                               })
            bs.gameTimer(60, light.delete)

            flash = bs.newNode("flash",
                               attrs={
                                   'position': punchPos,
                                   'size': 0.57 + 0.17 * hurtiness,
                                   'color': flashColor
                               })
            bs.gameTimer(60, flash.delete)

        if m.hitType == 'impact':
            bs.emitBGDynamics(position=m.pos,
                              velocity=(m.forceDirection[0] * 2.0,
                                        m.forceDirection[1] * 2.0,
                                        m.forceDirection[2] * 2.0),
                              count=min(10, 1 + int(damage * 0.01)),
                              scale=0.4,
                              spread=0.1)

        if self.hitPoints > 0:

            # its kinda crappy to die from impacts, so lets reduce impact damage
            # by a reasonable amount if it'll keep us alive
            if m.hitType == 'impact' and damage > self.hitPoints:
                # drop damage to whatever puts us at 10 hit points, or 200 less than it used to be
                # whichever is greater (so it *can* still kill us if its high enough)
                newDamage = max(damage - 200, self.hitPoints - 10)
                damage = newDamage

            self.node.handleMessage("flash")
            # if we're holding something, drop it
            if damage > 0.0 and self.node.holdNode.exists():
                self.node.holdNode = bs.Node(None)
            self.hitPoints -= damage
            self.node.hurt = 1.0 - float(self.hitPoints) / self.hitPointsMax
            # if we're cursed, *any* damage blows us up
            if self._cursed and damage > 0:
                bs.gameTimer(50, bs.WeakCall(self.curseExplode,
                                             m.sourcePlayer))
            # if we're frozen, shatter.. otherwise die if we hit zero
            if self.frozen and (damage > 200 or self.hitPoints <= 0):
                self.shatter()
            elif self.hitPoints <= 0:
                #if m.sourcePlayer.actor.enemyDrop:
                #   p = self.node.position
                #  def drop(v,p,lp,c):
                #     bsUtils.PopupText('Powerup{}\nDropped'.format('s' if len(lp) > 1 else ''),
                #                      position=p, color=c, scale=0.7).autoRetain()
                #   for l in lp:bsPowerup.Powerup(velocity=v,position=(p[0],p[1]+0.5,p[2]),powerupType=l,small=True).autoRetain()
                # if self.lastPowerup != []:
                #    bs.gameTimer(100,bs.Call(drop,self.node.velocity,p,self.lastPowerup,self.node.color))
                #   self.lastPowerup = []
                self.node.handleMessage(bs.DieMessage(how='impact'))

        # if we're dead, take a look at the smoothed damage val
        # (which gives us a smoothed average of recent damage) and shatter
        # us if its grown high enough

        if self.hitPoints <= 0:
            damageAvg = self.node.damageSmoothed * damageScale
            if damageAvg > 1000:
                self.shatter()

    elif isinstance(m, _BombDiedMessage):
        self.bombCount += 1

    elif isinstance(m, bs.DieMessage):
        wasDead = self._dead
        self._dead = True
        self.hitPoints = 0
        if m.immediate:
            self.node.delete()
        elif self.node.exists():
            if m.how == 'leftGame':
                if self.shattered:
                    pass

                def update():
                    try:
                        pos = self.node.position
                        self.node.handleMessage("impulse", pos[0],
                                                pos[1] + 0.5, pos[2], 0, 5, 0,
                                                3, 10, 0, 0, 0, 5, 0)
                    except:
                        pass

                delay = 0
                for i in range(40):
                    bs.gameTimer(delay, bs.Call(update))
                    delay += 50
            self.node.hurt = 1.0
            if self.playBigDeathSound and not wasDead:
                bs.playSound(self.getFactory().singlePlayerDeathSound)
            self.node.dead = True
            bs.gameTimer(2000, self.node.delete)

    elif isinstance(m, bs.OutOfBoundsMessage):
        # by default we just die here
        if hasattr(self, 'fallprotect'):
            if self.fallprotect:
                self.node.handleMessage(
                    bs.StandMessage(
                        self.getActivity().getMap().getFFAStartPosition(
                            self.getActivity().players)))
                bsUtils.PopupText(u'🐦FallProtection x 0',
                                  position=self.node.position,
                                  color=self.node.color,
                                  scale=1.0).autoRetain()
                self.fallprotect = False
            else:
                self.handleMessage(bs.DieMessage(how='fall'))
        else:
            self.handleMessage(bs.DieMessage(how='fall'))

    elif isinstance(m, bs.StandMessage):
        self._lastStandPos = (m.position[0], m.position[1], m.position[2])
        self.node.handleMessage("stand", m.position[0], m.position[1],
                                m.position[2], m.angle)

    elif isinstance(m, _FootConnectMessage):
        self.footing = True

    elif isinstance(m, _FootDisconnectMessage):
        self.footing = False

    elif isinstance(m, _CurseExplodeMessage):
        self.curseExplode()

    elif isinstance(m, _PunchHitMessage):

        node = bs.getCollisionInfo("opposingNode")

        # only allow one hit per node per punch
        if node is not None and node.exists(
        ) and not node in self._punchedNodes:

            punchMomentumAngular = self.node.punchMomentumAngular * self._punchPowerScale
            punchPower = self.node.punchPower * self._punchPowerScale

            # ok here's the deal:  we pass along our base velocity for use in the
            # impulse damage calculations since that is a more predictable value
            # than our fist velocity, which is rather erratic.
            # ...however we want to actually apply force in the direction our fist
            # is moving so it looks better.. so we still pass that along as a direction
            # ..perhaps a time-averased fist-velocity would work too?.. should try that.

            # if its something besides another spaz, just do a muffled punch sound
            if node.getNodeType() != 'spaz':
                sounds = self.getFactory().impactSoundsMedium
                sound = sounds[random.randrange(len(sounds))]
                bs.playSound(sound, 1.0, position=self.node.position)

            t = self.node.punchPosition
            punchDir = self.node.punchVelocity
            v = self.node.punchMomentumLinear

            self._punchedNodes.add(node)
            node.handleMessage(
                bs.HitMessage(pos=t,
                              velocity=v,
                              magnitude=punchPower * punchMomentumAngular *
                              110.0,
                              velocityMagnitude=punchPower * 40,
                              radius=0,
                              srcNode=self.node,
                              sourcePlayer=self.sourcePlayer,
                              forceDirection=punchDir,
                              hitType='punch',
                              hitSubType='superPunch'
                              if self._hasBoxingGloves else 'default'))

            # also apply opposite to ourself for the first punch only
            # ..this is given as a constant force so that it is more noticable for slower punches
            # where it matters.. for fast awesome looking punches its ok if we punch 'through' the target
            mag = -400.0
            if self._hockey:
                mag *= 0.5
            if len(self._punchedNodes) == 1:
                self.node.handleMessage("kickBack", t[0], t[1], t[2],
                                        punchDir[0], punchDir[1], punchDir[2],
                                        mag)

    elif isinstance(m, _PickupMessage):
        opposingNode, opposingBody = bs.getCollisionInfo(
            'opposingNode', 'opposingBody')

        if opposingNode is None or not opposingNode.exists():
            return True

        # dont allow picking up of invincible dudes
        try:
            if opposingNode.invincible == True:
                return True
        except Exception:
            pass

        # if we're grabbing the pelvis of a non-shattered spaz, we wanna grab the torso instead
        if opposingNode.getNodeType(
        ) == 'spaz' and not opposingNode.shattered and opposingBody == 4:
            opposingBody = 1

        elif opposingNode.getNodeType(
        ) == 'spaz' and opposingNode.frozen and not opposingNode.shattered and opposingBody == 0:
            opposingNode.handleMessage(bs.ShouldShatterMessage())
            bs.emitBGDynamics(position=opposingNode.position,
                              velocity=opposingNode.velocity,
                              count=int(random.random() * 10.0 + 10.0),
                              scale=0.7,
                              spread=0.4,
                              chunkType='ice')
            bs.emitBGDynamics(position=opposingNode.position,
                              velocity=opposingNode.velocity,
                              count=int(random.random() * 10.0 + 10.0),
                              scale=0.4,
                              spread=0.4,
                              chunkType='ice')

        # special case - if we're holding a flag, dont replace it
        # ( hmm - should make this customizable or more low level )
        held = self.node.holdNode
        if held is not None and held.exists() and held.getNodeType() == 'flag':
            return True

        self.node.holdBody = opposingBody  # needs to be set before holdNode
        self.node.holdNode = opposingNode
    else:
        bs.Actor.handleMessage(self, m)


def dropBomb(self):
    """
    Tell the spaz to drop one of his bombs, and returns
    the resulting bomb object.
    If the spaz has no bombs or is otherwise unable to
    drop a bomb, returns None.
    """

    if (self.landMineCount <= 0 and self.bombCount <= 0) or self.frozen:
        return
    p = self.node.positionForward
    v = self.node.velocity

    if self.landMineCount > 0:
        droppingBomb = False
        self.setLandMineCount(self.landMineCount - 1)
        bombType = 'landMine'
    elif self.forceBombCount > 0:
        droppingBomb = False
        self.setForceBombCount(self.forceBombCount - 1)
        bombType = 'forceBomb'
    elif self.triggerBombCount > 0:
        droppingBomb = False
        self.setTriggerBombCount(self.triggerBombCount - 1)
        bombType = 'triggerBomb'
    elif self.curseBombCount > 0:
        droppingBomb = False
        self.setcurseBombCount(self.curseBombCount - 1)
        bombType = 'curseBomb'
    else:
        droppingBomb = True
        bombType = self.bombType

    bomb = bs.Bomb(position=(p[0], p[1] - 0.0, p[2]),
                   velocity=(v[0], v[1], v[2]),
                   bombType=bombType,
                   blastRadius=self.blastRadius,
                   sourcePlayer=self.sourcePlayer,
                   owner=self.node).autoRetain()

    if droppingBomb:
        self.bombCount -= 1
        bomb.node.addDeathAction(
            bs.WeakCall(self.handleMessage, _BombDiedMessage()))

    self._pickUp(bomb.node)

    for c in self._droppedBombCallbacks:
        c(self, bomb)

    return bomb


def lightningBolt(self, position=(0, 10, 0), radius=10):
    bs.shakeCamera(2)
    tint = bs.getSharedObject('globals').tint
    light = bs.newNode('light',
                       attrs={
                           'position': position,
                           'color': (0.2, 0.2, 0.4),
                           'volumeIntensityScale': 1.0,
                           'radius': radius
                       })

    bsUtils.animate(
        light, "intensity", {
            0: 1,
            50: radius,
            150: radius / 2,
            250: 0,
            260: radius,
            410: radius / 2,
            510: 0
        })

    tint = bs.getSharedObject('globals').tint

    bsUtils.animateArray(bs.getSharedObject('globals'), "tint", 3, {
        0: tint,
        200: (0.5, 0.5, 0.5),
        500: tint
    })

    vout = bs.getSharedObject('globals').vignetteOuter

    bsUtils.animateArray(
        bs.getSharedObject('globals'), 'vignetteOuter', 3, {
            0: bs.getSharedObject('globals').vignetteOuter,
            250: (0.6, 0, 0),
            600: vout
        })

    bs.playSound(bs.getSound('explosion01'), volume=10, position=(0, 10, 0))

    bs.gameTimer(600, light.delete)


def _pickUp(self, node):
    if self.node.exists() and node.exists():
        self.node.holdBody = 0  # needs to be set before holdNode
        self.node.holdNode = node


def setLandMineCount(self, count):
    """
    Set the number of land-mines this spaz is carrying.
    """
    self.landMineCount = count
    if self.node.exists():
        if self.landMineCount != 0:
            self.node.counterText = 'x' + str(self.landMineCount)
            self.node.counterTexture = bs.Powerup.getFactory().texLandMines
        else:
            self.node.counterText = ''


def setcurseBombCount(self, count):
    """
    Set the number of land-mines this spaz is carrying.
    """
    self.curseBombCount = count
    if self.node.exists():
        if self.curseBombCount != 0:
            self.node.counterText = 'x' + str(self.curseBombCount)
            self.node.counterTexture = bs.Powerup.getFactory().texcurseBomb
        else:
            self.node.counterText = ''


def setTrailblazerCount(self, count):
    """
    Set the number of land-mines this spaz is carrying.
    """
    self.trailblazerCount = count
    if self.node.exists():
        if self.trailblazerCount != 0:
            self.node.counterText = 'x' + str(self.trailblazerCount)
            self.node.counterTexture = bs.Powerup.getFactory().texQuake
        else:
            self.node.counterText = ''


def setForceBombCount(self, count):
    """
    Set the number of land-mines this spaz is carrying.
    """
    self.forceBombCount = count
    if self.node.exists():
        if self.forceBombCount != 0:
            self.node.counterText = 'x' + str(self.forceBombCount)
            self.node.counterTexture = bs.Powerup.getFactory().texHeatSeeker
        else:
            self.node.counterText = ''


def _getBombTypeTex(self):
    bombFactory = bs.Powerup.getFactory()
    if self.bombType == 'sticky': return bombFactory.texStickyBombs
    elif self.bombType == 'ice': return bombFactory.texIceBombs
    elif self.bombType == 'impact': return bombFactory.texImpactBombs
    elif self.bombType == 'cluster': return bombFactory.texClusterBombs
    else: raise Exception()


def setTriggerBombCount(self, count):
    """
    Set the number of land-mines this spaz is carrying.
    """
    self.triggerBombCount = count
    if self.node.exists():
        if self.triggerBombCount != 0:
            self.node.counterText = 'x' + str(self.triggerBombCount)
            self.node.counterTexture = bs.Powerup.getFactory().texTriggerBombs
        else:
            self.node.counterText = ''


def curseExplode(self, sourcePlayer=None):
    """
    Explode the poor spaz as happens when
    a curse timer runs out.
    """

    # convert None to an empty player-ref
    if sourcePlayer is None:
        sourcePlayer = bs.Player(None)

    if self._cursed and self.node.exists():
        self.shatter(extreme=True)
        self.handleMessage(bs.DieMessage())
        activity = self._activity()
        if activity:
            bs.Blast(position=self.node.position,
                     velocity=self.node.velocity,
                     blastRadius=3.0,
                     blastType='normal',
                     sourcePlayer=sourcePlayer if sourcePlayer.exists() else
                     self.sourcePlayer).autoRetain()
        # if bs.getSharedObject('globals').slowMotion == False:
        #   def slowMo():
        #      bs.getSharedObject('globals').slowMotion = bs.getSharedObject('globals').slowMotion == False
        # slowMo()
        # bs.gameTimer(600,bs.Call(slowMo))
        else:
            pass
        self._cursed = False


def _invisibilityWearOffFlash(self):
    if self.node.exists():
        self.node.billboardTexture = bs.Powerup.getFactory().texRainbow
        self.node.billboardOpacity = 1.0
        self.node.billboardCrossOut = True


def _invisibilityWearOff(self):
    try:
        factory = self.getFactory()
        self.node.name = self._name
        self.node.style = self._style
        self.node.headModel = self._head
        self.node.torsoModel = self._torso
        self.node.pelvisModel = self._pelvis
        self.node.upperArmModel = self._upperArm
        self.node.foreArmModel = self._foreArm
        self.node.handModel = self._hand
        self.node.upperLegModel = self._upperLeg
        self.node.lowerLegModel = self._lowerLeg
        self.node.toesModel = self._toes
        try:
            self.effect._Text.scale = self._effectscale
        except:
            pass
        self.invisible = False
        self.hp._Text.scale = self._hpscale
        if self.node.exists():
            self.node.billboardOpacity = 0.0
    except:
        pass


bsSpaz.Spaz.onPunchPress = onPunchPress
bsSpaz.Spaz.onJumpPress = onJumpPress
bsSpaz.SpazFactory.__init__ = SpazFactory__init__
bsSpaz.Spaz.onJumpRelease = onJumpRelease
bsSpaz.Spaz.setInvisibility = setInvisibility
bsSpaz.Spaz.handleMessage = handleMessage
bsSpaz.Spaz.dropBomb = dropBomb
bsSpaz.Spaz.lightningBolt = lightningBolt
bsSpaz.Spaz._pickUp = _pickUp
bsSpaz.Spaz.setLandMineCount = setLandMineCount
bsSpaz.Spaz.setTrailblazerCount = setTrailblazerCount
bsSpaz.Spaz.setcurseBombCount = setcurseBombCount
bsSpaz.Spaz.setForceBombCount = setForceBombCount
bsSpaz.Spaz.setTriggerBombCount = setTriggerBombCount
bsSpaz.Spaz.curseExplode = curseExplode
bsSpaz.Spaz._invisibilityWearOff = _invisibilityWearOff
bsSpaz.Spaz._invisibilityWearOffFlash = _invisibilityWearOffFlash
bsSpaz.Spaz._getBombTypeTex = _getBombTypeTex

#######END##########


class SurroundBallFactory(object):
    def __init__(self):
        self.bonesTex = bs.getTexture("bonesColor")
        self.bonesModel = bs.getModel("bonesHead")
        self.bearTex = bs.getTexture("bearColor")
        self.bearModel = bs.getModel("bearHead")
        self.aliTex = bs.getTexture("aliColor")
        self.aliModel = bs.getModel("aliHead")
        self.b9000Tex = bs.getTexture("cyborgColor")
        self.b9000Model = bs.getModel("cyborgHead")
        self.frostyTex = bs.getTexture("frostyColor")
        self.frostyModel = bs.getModel("frostyHead")
        self.cubeTex = bs.getTexture("crossOutMask")
        self.cubeModel = bs.getModel("powerup")
        try:
            self.mikuModel = bs.getModel("operaSingerHead")
            self.mikuTex = bs.getTexture("operaSingerColor")
        except:
            bs.PrintException()

        self.ballMaterial = bs.Material()
        self.impactSound = bs.getSound("impactMedium")
        self.ballMaterial.addActions(actions=("modifyNodeCollision", "collide",
                                              False))


class SurroundBall(bs.Actor):
    def __init__(self, spaz, shape="bones"):
        if spaz is None or not spaz.isAlive():
            return

        bs.Actor.__init__(self)

        self.spazRef = weakref.ref(spaz)

        factory = self.getFactory()

        s_model, s_texture = {
            "bones": (factory.bonesModel, factory.bonesTex),
            "bear": (factory.bearModel, factory.bearTex),
            "ali": (factory.aliModel, factory.aliTex),
            "b9000": (factory.b9000Model, factory.b9000Tex),
            "miku": (factory.mikuModel, factory.mikuTex),
            "frosty": (factory.frostyModel, factory.frostyTex),
            "RedCube": (factory.cubeModel, factory.cubeTex)
        }.get(shape, (factory.bonesModel, factory.bonesTex))

        self.snode = bs.newNode(
            "prop",
            owner=spaz.node,
            attrs={
                "model":
                s_model,
                "body":
                "sphere",
                "colorTexture":
                s_texture,
                "reflection":
                "soft",
                "modelScale":
                0.5,
                "bodyScale":
                0.1,
                "density":
                0.1,
                "reflectionScale": [0.15],
                "shadowSize":
                0.6,
                "position": (spaz.node.position[0], spaz.node.position[1] + 10,
                             spaz.node.position[2]),
                "velocity": (0, 0, 0),
                "materials":
                [bs.getSharedObject("objectMaterial"), factory.ballMaterial]
            },
            delegate=self)

        self.surroundTimer = None
        self.surroundRadius = 0.7
        self.angleDelta = math.pi / 12.0
        self.curAngle = random.random() * math.pi * 2.0
        self.curHeight = 0.0
        self.curHeightDir = 1
        self.heightDelta = 0.2
        self.heightMax = 1.0
        self.heightMin = 0.1
        self.initTimer(spaz.node.position)

    def getTargetPosition(self, spazPos):
        p = spazPos
        pt = (p[0] + self.surroundRadius * math.cos(self.curAngle),
              p[1] + self.curHeight,
              p[2] + self.surroundRadius * math.sin(self.curAngle))
        self.curAngle += self.angleDelta
        self.curHeight += self.heightDelta * self.curHeightDir
        if self.curHeight > self.heightMax or self.curHeight < self.heightMin:
            self.curHeightDir = -self.curHeightDir

        return pt

    def initTimer(self, p):
        self.snode.position = p
        self.snode.position = self.getTargetPosition(p)
        self.surroundTimer = bs.Timer(30,
                                      bs.WeakCall(self.circleMove),
                                      repeat=True)

    def circleMove(self):
        spaz = self.spazRef()
        if spaz is None or not spaz.isAlive() or not spaz.node.exists():
            self.handleMessage(bs.DieMessage())
            return
        p = spaz.node.position
        pt = self.getTargetPosition(p)
        pn = self.snode.position
        d = [pt[0] - pn[0], pt[1] - pn[1], pt[2] - pn[2]]
        if abs(d[0] + d[1] + d[2]) > 2:
            self.snode.position = p
        speed = self.getMaxSpeedByDir(d)
        self.snode.velocity = speed

    @staticmethod
    def getMaxSpeedByDir(direction):
        k = 7.0 / max((abs(x) for x in direction))
        return tuple(x * k for x in direction)

    def handleMessage(self, m):
        bs.Actor.handleMessage(self, m)
        if isinstance(m, bs.DieMessage):
            if self.surroundTimer is not None:
                self.surroundTimer = None
            self.snode.delete()
        elif isinstance(m, bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())

    def getFactory(cls):
        activity = bs.getActivity()
        if activity is None:
            raise Exception("no current activity")
        try:
            return activity._sharedSurroundBallFactory
        except Exception:
            f = activity._sharedSurroundBallFactory = SurroundBallFactory()
            return f


class PermissionEffect(object):
    def __init__(self,
                 position=(0, 1.55, 0),
                 owner=None,
                 prefix='',
                 prefixColor=(1, 1, 1),
                 prefixAnim={
                     0: (1, 1, 1),
                     500: (0.5, 0.5, 0.5)
                 },
                 prefixAnimate=False,
                 particles=False):
        self.position = position
        self.owner = owner

        # nick
        # text
        # color
        # anim
        # animCurve
        # particles

        def a():
            self.emit()

        # particles
        if particles:
            self.timer = bs.Timer(10, bs.Call(a), repeat=True)

        # prefix
        m = bs.newNode('math',
                       owner=self.owner,
                       attrs={
                           'input1': self.position,
                           'operation': 'add'
                       })
        self.owner.connectAttr('position', m, 'input2')

        self._Text = bs.newNode(
            'text',
            owner=self.owner,
            attrs={
                'text': prefix,  # prefix text
                'inWorld': True,
                'shadow': 1.2,
                'flatness': 1.0,
                'color': prefixColor,
                'scale': 0.0,
                'hAlign': 'center'
            })

        m.connectAttr('output', self._Text, 'position')

        # smooth prefix spawn
        bs.animate(self._Text, 'scale', {0: 0.0, 1000: 0.01})

        # animate prefix
        if prefixAnimate:
            bsUtils.animateArray(self._Text, 'color', 3, prefixAnim,
                                 True)  # animate prefix color

    def emit(self):
        if self.owner.exists():
            vel = 2
            bs.emitBGDynamics(
                position=(self.owner.torsoPosition[0] - 0.25 +
                          random.random() * 0.5, self.owner.torsoPosition[1] -
                          0.25 + random.random() * 0.5,
                          self.owner.torsoPosition[2] - 0.25 +
                          random.random() * 0.5),
                velocity=((-vel + (random.random() *
                                   (vel * 2))) + self.owner.velocity[0] * 2,
                          (-vel + (random.random() *
                                   (vel * 2))) + self.owner.velocity[1] * 3,
                          (-vel + (random.random() *
                                   (vel * 2))) + self.owner.velocity[2] * 2),
                count=10,
                scale=0.3,
                spread=0.06,
                chunkType='spark')
            # emitType = 'stickers')


def catchphrase(self,custom=None):
    """
    Show a random catchphrase above player's head
    """
    if not self.node.exists() and self.duringCatchphrase:
        return
    if random.randint(0, 1) or custom is not None:
        self._catchphraseText.text = random.choice(some.catchphrases) if custom is None else custom

        def sound():
            self.node.handleMessage(
                random.choice(['celebrate', 'celebrateL', 'celebrateR']), 1000)
            self.node.handleMessage("attackSound")

        # bs.playSound(random.choice(self.getFactory()._getMedia(self._character)['jumpSounds']),1.5,self.node.position)
        time = 0
        self.soundTimer = bs.Timer(time, bs.Call(sound))
        self.duringCatchphrase = True

        def _timeout():
            self.duringCatchphrase = False

        bs.animate(self._catchphraseText,
                   'scale', {
                       time: 0,
                       time + 150: 0.015,
                       time + 300: 0.010,
                       time + 1000: 0.010,
                       time + 1200: 0.0
                   },
                   loop=False)
        bs.gameTimer(time + 1000, _timeout)


def __init__(self,
             color=(1, 1, 1),
             highlight=(0.5, 0.5, 0.5),
             character="Spaz",
             player=None,
             powerupsExpire=True):
    """
    Create a spaz for the provided bs.Player.
    Note: this does not wire up any controls;
    you must call connectControlsToPlayer() to do so.
    """
    # convert None to an empty player-ref
    if player is None:
        player = bs.Player(None)

    bs.Spaz.__init__(self,
                     color=color,
                     highlight=highlight,
                     character=character,
                     sourcePlayer=player,
                     startInvincible=True,
                     powerupsExpire=powerupsExpire)
    self.lastPlayerAttackedBy = None  # FIXME - should use empty player ref
    self.lastAttackedTime = 0
    self.lastAttackedType = None
    self.heldCount = 0
    self.lastPlayerHeldBy = None  # FIXME - should use empty player ref here
    self._player = player
    self.punchPowerScale = 1.3

    if player.exists():
        playerNode = bs.getActivity()._getPlayerNode(player)
        self.node.connectAttr('torsoPosition', playerNode, 'position')
    self.lighting = bs.newNode('light',
                               owner=self.node,
                               attrs={
                                   'position': (self.node.position),
                                   'color': self.node.color,
                                   'volumeIntensityScale':
                                   1.2 if some.night else 0.01,
                                   'radius': 0.085 if some.night else 0.01
                               })

    self.node.connectAttr('position', self.lighting, 'position')

    self.decorate(player)

    # grab the node for this player and wire it to follow our spaz (so players' controllers know where to draw their guides, etc)


def decorate(self, player):
    p = player.get_account_id()
    self.triggerBombs = []
    if p is None: return

    try:
        stuff = db.getData(p)
        items = stuff['i']
        tag = '' if not some.show_tag else bs.utf8(stuff['t'])
        rank = db.getRank(p)
    except Exception as e:
        print e
        items = []
        rank = 20000
    if 'logicon' in items:
        character = 'Logicon'
    self.luck = False
    self.effect = None
    self.companion = None
    self.backflip = False
    self.backflipProtection = False
    self.backflipPresent = False
    '''
        if 'logiconn' in items:
                self._character = bsSpaz.appearances['Logicon']
                # self.node.colorTexture = bs.getTexture('cyborgColor')
                # self.node.colorMaskTexture = bs.getTexture("neoSpazColorMask")
                # self.node.headModel = bs.getModel("cyborgHead")

                self.node.headModel = bs.getModel(self._character.headModel)
                self.node.torsoModel = bs.getModel(self._character.torsoModel)
                self.node.pelvisModel = bs.getModel(self._character.pelvisModel)
                self.node.upperArmModel = bs.getModel(self._character.upperArmModel)
                self.node.foreArmModel = bs.getModel(self._character.foreArmModel)
                self.node.handModel = bs.getModel(self._character.handModel)
                self.node.upperLegModel = bs.getModel(self._character.upperLegModel)
                self.node.lowerLegModel = bs.getModel(self._character.lowerLegModel)
                self.node.toesModel = bs.getModel(self._character.toesModel)
                self.node.colorTexture = bs.getTexture(self._character.colorTexture)
                self.node.colorMaskTexture = bs.getTexture(self._character.colorMaskTexture)
                self.node.style = self._character.style
        '''
    if p is None:
        return
    if 'impact' in items:
        self.bombType = self.bombTypeDefault = self.defaultBombType = 'impact'
    if 'rainbow' in items:
        bsUtils.animateArray(self.node, 'color', 3, {
            0: (1, 0, 0),
            250: (0, 1, 0),
            250 * 2: (0, 0, 1),
            250 * 3: (1, 0, 0)
        }, True)
    if 'particles' in items:
        self.effect = PermissionEffect(owner=self.node, particles=True)

    if 'tag' in items and tag is not '' and not self.luck:
        self.effect = PermissionEffect(owner=self.node,
                                       prefix=bs.utf8(tag),
                                       prefixAnim={
                                           0: (2, 1, 1),
                                           250: (1, 2, 1),
                                           250 * 2: (1, 1, 2),
                                           250 * 3: (2, 1, 1)
                                       },
                                       prefixAnimate=True)
        self.luck = True
#        if p in some.admins and not self.luck:
#           self.effect = PermissionEffect(owner = self.node,prefix = bs.utf8(u'\ue043MODERATOR\ue043'),prefixAnim = {0: (2,0,0), 250: (0,2,0),250*2:(0,0,2),250*3:(3,0,0)},prefixAnimate = True)
#          self.luck = True
    if not self.luck and some.show_rank:
        if rank <= 10:
            self.effect = PermissionEffect(
                owner=self.node,
                prefix=bs.utf8(u'\ue048#{0}\ue048').format(rank),
                prefixAnim={
                    0: (2, 1, 1),
                    250: (1, 2, 1),
                    250 * 2: (1, 1, 2),
                    250 * 3: (2, 1, 1)
                },
                prefixAnimate=True)
        else:
            self.effect = PermissionEffect(owner=self.node,
                                           prefix=u'#{0}'.format(rank))
        self.luck = True
    if 'companion' in items:
        self.companion = SurroundBall(self, shape="bones")


#    if 'enemy-drops' in items:
#       self.enemyDrop = True
    if 'fall-protection' in items:
        self.fallprotect = True
    if 'backflip' in items:
        self.backflip = True
        self.backflipPresent = True
    if 'backflip-protection' in items:
        self.backflipProtection = True
    if 'recover' in items:

        def health_increase():
            if self.isAlive():
                self.hitPoints = min(self.hitPointsMax, self.hitPoints + 50)

        self.health_increase_timer = bs.Timer(1000,
                                              bs.Call(health_increase),
                                              repeat=True)
    if some.show_hp:
        self.hp = PermissionEffect(owner=self.node,
                                   prefix='HP: ' +
                                   str(int(self.hitPoints / 10)),
                                   position=(0, 1.25, 0))

        def refresh_hp():
            self.hp._Text.text = 'HP: ' + str(int(self.hitPoints / 10))
            self.hp._Text.color = (1, self.hitPoints / 1000,
                                   self.hitPoints / 1000)
            if self.isAlive():
                self.hptimer = bs.Timer(50, bs.Call(refresh_hp))

        self.hptimer = bs.Timer(50, bs.Call(refresh_hp))

    self.lastPos = self.node.position
    if 'footprints' in items:

        def doCirle():
            if self.isAlive() and self.footing and not self.invisible:
                p = self.node.position
                p2 = self.lastPos
                diff = (bs.Vector(p[0] - p2[0], 0.0, p[2] - p2[2]))
                dist = (diff.length())
                if dist > 0.2:
                    c = self.node.highlight
                    r = bs.newNode('locator',
                                   attrs={
                                       'shape': 'circle',
                                       'position': p,
                                       'color': self.node.color if c else
                                       (5, 5, 5),
                                       'opacity': 1,
                                       'drawBeauty': False,
                                       'additive': False,
                                       'size': [0.15]
                                   })
                    bsUtils.animateArray(r, 'size', 1, {
                        0: [0.15],
                        2500: [0.15],
                        3000: [0]
                    })
                    bs.gameTimer(3000, r.delete)
                    self.lastPos = self.node.position

        bs.gameTimer(200, bs.Call(doCirle), repeat=True)

    self._catchphraseTextOffset = bs.newNode('math',
                                             owner=self.node,
                                             attrs={
                                                 'input1': (0.0, 2.3, -0.15),
                                                 'operation': 'add'
                                             })
    self.node.connectAttr('torsoPosition', self._catchphraseTextOffset,
                          'input2')

    self._catchphraseText = bs.newNode('text',
                                       owner=self.node,
                                       attrs={
                                           'inWorld': True,
                                           'text': '',
                                           'scale': 0.0,
                                           'shadow': 1.0,
                                           'maxWidth': 250,
                                           'color': (1, 1, 1),
                                           'vAlign': 'top',
                                           'hAlign': 'center'
                                       })
    self._catchphraseTextOffset.connectAttr('output', self._catchphraseText,
                                            'position')
    self._catchphraseText.opacity = 0.8

    timeout = 60000

    def AFK_check(to):
        t = bs.getRealTime()
        #print t,self.lastChangeTime,t-self.lastChangeTime
        if self.isAlive() and t - self.lastChangeTime > to:
            bs.screenMessage(
                u'Removing {} for being AFK for more than {} seconds.'.format(
                    player.getName(), int(to / 1000)))
            player.removeFromGame()

    self.afk_checker = bs.Timer(timeout + 1000,
                                bs.Call(AFK_check, timeout),
                                timeType='net',
                                repeat=True)

bsSpaz.PermissionEffect = PermissionEffect
bsSpaz.PlayerSpaz.catchphrase = catchphrase
bsSpaz.PlayerSpaz.decorate = decorate
bsSpaz.PlayerSpaz.__init__ = __init__
# bsSpaz.PlayerSpaz.refresh_hp = refresh_hp

bsSpaz.Spaz.onPickUpPress = onPickUpPress
bsSpaz.Spaz.onPickUpRelease = onPickUpRelease
bsSpaz.Spaz._onHoldPositionPress = _onHoldPositionPress
bsSpaz.Spaz._onHoldPositionRelease = _onHoldPositionRelease
bsSpaz.Spaz.onPunchPress = onPunchPress
bsSpaz.Spaz.onPunchRelease = onPunchRelease
bsSpaz.Spaz.onBombPress = onBombPress
bsSpaz.Spaz.onBombRelease = onBombRelease
bsSpaz.Spaz.onRun = onRun
bsSpaz.Spaz.onFlyPress = onFlyPress
bsSpaz.Spaz.onFlyRelease = onFlyRelease
bsSpaz.Spaz.onMove = onMove
bsSpaz.Spaz.onMoveUpDown = onMoveUpDown
bsSpaz.Spaz.onMoveLeftRight = onMoveLeftRight
