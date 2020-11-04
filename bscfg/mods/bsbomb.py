import random
import weakref
import some
import bs
import bsBomb
import bsUtils
import portalObjects
from bsBomb import Bomb, ExplodeMessage, ArmMessage, WarnMessage, Blast, BombFactory, \
    ExplodeHitMessage, ImpactMessage, SplatMessage
from bsVector import Vector
import bsInternal

bombTypes = [
    'ice', 'impact', 'landMine', 'normal', 'sticky', 'forceBomb',
    'triggerBomb', 'curseBomb', 'tnt', 'cluster'
]


class NewBombFactory(BombFactory):
    def __init__(self):
        """
        Instantiate a BombFactory.
        You shouldn't need to do this; call bs.Bomb.getFactory() to get a shared instance.
        """
        BombFactory.__init__(self)
        if some.custom_tnt: self.tntModel = bs.getModel('bomb')
        self.curseBombModel = bs.getModel('bomb')

        self.forceTex = bs.getTexture('egg2')
        if some.custom_tnt: self.tntTex = bs.getTexture('powerupCurse')
        self.curseBombTex = bs.getTexture('powerupCurse')
        self.triggerBombTex = bs.getTexture('egg4')
        self.clusterBombTex = bs.getTexture("achievementWall")

        self.bombModel = bs.getModel('bomb')
        self.stickyBombModel = bs.getModel('bombSticky')
        self.impactBombModel = bs.getModel('impactBomb')
        self.landMineModel = bs.getModel('landMine')

        self.regularTex = bs.getTexture('bombColor')
        self.iceTex = bs.getTexture('bombColorIce')
        self.stickyTex = bs.getTexture('bombStickyColor')
        self.impactTex = bs.getTexture('impactBombColor')
        self.impactLitTex = bs.getTexture('impactBombColorLit')
        self.landMineTex = bs.getTexture('landMine')
        self.landMineLitTex = bs.getTexture('landMineLit')

        self.hissSound = bs.getSound('hiss')
        self.debrisFallSound = bs.getSound('debrisFall')
        self.woodDebrisFallSound = bs.getSound('woodDebrisFall')

        self.explodeSounds = (bs.getSound('explosion01'),
                              bs.getSound('explosion02'),
                              bs.getSound('explosion03'),
                              bs.getSound('explosion04'),
                              bs.getSound('explosion05'))

        self.freezeSound = bs.getSound('freeze')
        self.fuseSound = bs.getSound('fuse01')
        self.activateSound = bs.getSound('activateBeep')
        self.warnSound = bs.getSound('warnBeep')
        self.curseBombSound = bs.getSound('freeze')

        # set up our material so new bombs dont collide with objects
        # that they are initially overlapping
        self.bombMaterial = bs.Material()
        self.normalSoundMaterial = bs.Material()
        self.stickyMaterial = bs.Material()

        self.bombMaterial.addActions(
            conditions=((('weAreYoungerThan', 100), 'or',
                         ('theyAreYoungerThan', 100)), 'and',
                        ('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial'))),
            actions=(('modifyNodeCollision', 'collide', False)))

        # we want pickup materials to always hit us even if we're currently not
        # colliding with their node (generally due to the above rule)
        self.bombMaterial.addActions(
            conditions=('theyHaveMaterial',
                        bs.getSharedObject('pickupMaterial')),
            actions=(('modifyPartCollision', 'useNodeCollide', False)))

        self.bombMaterial.addActions(actions=('modifyPartCollision',
                                              'friction', 0.3))

        self.landMineNoExplodeMaterial = bs.Material()
        self.landMineBlastMaterial = bs.Material()
        self.landMineBlastMaterial.addActions(
            conditions=(('weAreOlderThan', 200), 'and',
                        ('theyAreOlderThan', 200), 'and', ('evalColliding', ),
                        'and', (('theyDontHaveMaterial',
                                 self.landMineNoExplodeMaterial), 'and',
                                (('theyHaveMaterial',
                                  bs.getSharedObject('objectMaterial')), 'or',
                                 ('theyHaveMaterial',
                                  bs.getSharedObject('playerMaterial'))))),
            actions=(('message', 'ourNode', 'atConnect', ImpactMessage())))

        self.impactBlastMaterial = bs.Material()
        self.impactBlastMaterial.addActions(
            conditions=(('weAreOlderThan', 200), 'and',
                        ('theyAreOlderThan', 200), 'and', ('evalColliding', ),
                        'and', (('theyHaveMaterial',
                                 bs.getSharedObject('footingMaterial')), 'or',
                                ('theyHaveMaterial',
                                 bs.getSharedObject('objectMaterial')))),
            actions=(('message', 'ourNode', 'atConnect', ImpactMessage())))

        self.blastMaterial = bs.Material()
        self.blastMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial'))),
            actions=(('modifyPartCollision', 'collide',
                      True), ('modifyPartCollision', 'physical', False),
                     ('message', 'ourNode', 'atConnect', ExplodeHitMessage())))

        self.dinkSounds = (bs.getSound('bombDrop01'),
                           bs.getSound('bombDrop02'))
        self.stickyImpactSound = bs.getSound('stickyImpact')

        self.rollSound = bs.getSound('bombRoll01')

        # collision sounds
        self.normalSoundMaterial.addActions(
            conditions=('theyHaveMaterial',
                        bs.getSharedObject('footingMaterial')),
            actions=(('impactSound', self.dinkSounds, 2, 0.8),
                     ('rollSound', self.rollSound, 3, 6)))

        self.stickyMaterial.addActions(actions=(('modifyPartCollision',
                                                 'stiffness', 0.1),
                                                ('modifyPartCollision',
                                                 'damping', 1.0)))

        self.stickyMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial')), 'or',
                        ('theyHaveMaterial',
                         bs.getSharedObject('footingMaterial'))),
            actions=(('message', 'ourNode', 'atConnect', SplatMessage())))


def __init__(self,
             position=(0, 1, 0),
             velocity=(0, 0, 0),
             blastRadius=2.0,
             blastType="normal",
             sourcePlayer=None,
             hitType='explosion',
             hitSubType='normal'):
    """
    Instantiate with given values.
    """
    bs.Actor.__init__(self)

    factory = NewBomb.getFactory()

    self.blastType = blastType
    self.sourcePlayer = sourcePlayer

    self.hitType = hitType
    self.hitSubType = hitSubType

    # blast radius
    self.radius = blastRadius

    self.node = bs.newNode(
        'region',
        attrs={
            'position':
            (position[0], position[1] - 0.1,
             position[2]),  # move down a bit so we throw more stuff upward
            'scale': (self.radius, self.radius, self.radius),
            'type':
            'sphere',
            'materials':
            (factory.blastMaterial, bs.getSharedObject('attackMaterial'))
        },
        delegate=self)

    bs.gameTimer(50, self.node.delete)

    # throw in an explosion and flash
    explosion = bs.newNode("explosion",
                           attrs={
                               'position':
                               position,
                               'velocity':
                               (velocity[0], max(-1.0,
                                                 velocity[1]), velocity[2]),
                               'radius':
                               self.radius,
                               'big': (self.blastType == 'tnt')
                           })
    if self.blastType == "ice":
        explosion.color = (0, 0.05, 0.4)

    bs.gameTimer(1000, explosion.delete)

    if self.blastType != 'ice':
        bs.emitBGDynamics(position=position,
                          velocity=velocity,
                          count=int(1.0 + random.random() * 4),
                          emitType='tendrils',
                          tendrilType='thinSmoke')
    bs.emitBGDynamics(
        position=position,
        velocity=velocity,
        count=int(4.0 + random.random() * 4),
        emitType='tendrils',
        tendrilType='ice' if self.blastType == 'ice' else 'smoke')
    bs.emitBGDynamics(position=position,
                      emitType='distortion',
                      spread=1.0 if self.blastType == 'tnt' else 2.0)

    # and emit some shrapnel..
    if self.blastType == 'ice':

        def _doEmit():
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=30,
                              spread=2.0,
                              scale=0.4,
                              chunkType='ice',
                              emitType='stickers')

        bs.gameTimer(50, _doEmit)  # looks better if we delay a bit

    elif self.blastType == 'sticky':

        def _doEmit():
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=int(4.0 + random.random() * 8),
                              spread=0.7,
                              chunkType='slime')
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=int(4.0 + random.random() * 8),
                              scale=0.5,
                              spread=0.7,
                              chunkType='slime')
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=15,
                              scale=0.6,
                              chunkType='slime',
                              emitType='stickers')
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=20,
                              scale=0.7,
                              chunkType='spark',
                              emitType='stickers')
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=int(6.0 + random.random() * 12),
                              scale=0.8,
                              spread=1.5,
                              chunkType='spark')

        bs.gameTimer(50, _doEmit)  # looks better if we delay a bit

    elif self.blastType == 'impact':  # regular bomb shrapnel

        def _doEmit():
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=int(4.0 + random.random() * 8),
                              scale=0.8,
                              chunkType='metal')
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=int(4.0 + random.random() * 8),
                              scale=0.4,
                              chunkType='metal')
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=20,
                              scale=0.7,
                              chunkType='spark',
                              emitType='stickers')
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=int(8.0 + random.random() * 15),
                              scale=0.8,
                              spread=1.5,
                              chunkType='spark')

        bs.gameTimer(50, _doEmit)  # looks better if we delay a bit

    else:  # regular or land mine bomb shrapnel

        def _doEmit():
            if self.blastType != 'tnt':
                bs.emitBGDynamics(position=position,
                                  velocity=velocity,
                                  count=int(4.0 + random.random() * 8),
                                  chunkType='rock')
                bs.emitBGDynamics(position=position,
                                  velocity=velocity,
                                  count=int(4.0 + random.random() * 8),
                                  scale=0.5,
                                  chunkType='rock')
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=30,
                              scale=1.0 if self.blastType == 'tnt' else 0.7,
                              chunkType='spark',
                              emitType='stickers')
            bs.emitBGDynamics(position=position,
                              velocity=velocity,
                              count=int(18.0 + random.random() * 20),
                              scale=1.0 if self.blastType == 'tnt' else 0.8,
                              spread=1.5,
                              chunkType='spark')

            # tnt throws splintery chunks
            if self.blastType == 'tnt':

                def _emitSplinters():
                    bs.emitBGDynamics(position=position,
                                      velocity=velocity,
                                      count=int(20.0 + random.random() * 25),
                                      scale=0.8,
                                      spread=1.0,
                                      chunkType='splinter')

                bs.gameTimer(10, _emitSplinters)

            # every now and then do a sparky one
            if self.blastType == 'tnt' or random.random() < 0.1:

                def _emitExtraSparks():
                    bs.emitBGDynamics(position=position,
                                      velocity=velocity,
                                      count=int(10.0 + random.random() * 20),
                                      scale=0.8,
                                      spread=1.5,
                                      chunkType='spark')

                bs.gameTimer(20, _emitExtraSparks)

        bs.gameTimer(0, _doEmit)  # looks better if we delay a bit

    light = bs.newNode('light',
                       attrs={
                           'position':
                           position,
                           'color':
                           (0.6, 0.6, 1.0) if self.blastType == 'ice' else
                           (1.0, 0.3, 0.1),
                           'volumeIntensityScale':
                           10.0
                       })

    s = random.uniform(0.6, 0.9)
    scorchRadius = lightRadius = self.radius
    if self.blastType == 'tnt':
        lightRadius *= 1.4
        scorchRadius *= 1.15
        s *= 3.0

    iScale = 1.6
    bsUtils.animate(
        light, "intensity", {
            0: 2.0 * iScale,
            int(s * 20): 0.1 * iScale,
            int(s * 25): 0.2 * iScale,
            int(s * 50): 17.0 * iScale,
            int(s * 60): 5.0 * iScale,
            int(s * 80): 4.0 * iScale,
            int(s * 200): 0.6 * iScale,
            int(s * 2000): 0.00 * iScale,
            int(s * 3000): 0.0
        })
    bsUtils.animate(
        light, "radius", {
            0: lightRadius * 0.2,
            int(s * 50): lightRadius * 0.55,
            int(s * 100): lightRadius * 0.3,
            int(s * 300): lightRadius * 0.15,
            int(s * 1000): lightRadius * 0.05
        })
    bs.gameTimer(int(s * 60000), light.delete)


class NewBomb(Bomb):
    """
    category: Game Flow Classes

    A bomb and its variants such as land-mines and tnt-boxes.
    """
    def __init__(self,
                 position=(0, 1, 0),
                 velocity=(0, 0, 0),
                 bombType='normal',
                 blastRadius=2.0,
                 sourcePlayer=None,
                 owner=None,
                 modelSize=1,
                 modelScale=1,
                 fuseTime=3000):
        """
        Create a new Bomb.

        bombType can be 'ice','impact','landMine','normal','sticky', or 'tnt'.
        Note that for impact or landMine bombs you have to call arm()
        before they will go off.
        """
        bs.Actor.__init__(self)

        factory = self.getFactory()

        if not bombType in bombTypes:
            raise Exception("invalid bomb type: " + bombType)
        self.bombType = bombType

        self._exploded = False

        if self.bombType == 'sticky' or self.bombType == 'forceBomb' or self.bombType == 'triggerBomb':
            self._lastStickySoundTime = 0

        self.blastRadius = blastRadius
        if self.bombType == 'ice':
            self.blastRadius *= 1.2
        elif self.bombType == 'impact':
            self.blastRadius *= 0.7
        elif self.bombType == 'landMine':
            self.blastRadius *= 0.7
        elif self.bombType == 'tnt':
            self.blastRadius *= 2.45
        elif self.bombType == "cluster":
            self.blastRadius *= 0.8

        self._explodeCallbacks = []

        # the player this came from
        self.sourcePlayer = sourcePlayer

        # by default our hit type/subtype is our own, but we pick up types of whoever
        # sets us off so we know what caused a chain reaction
        self.hitType = 'explosion'
        self.hitSubType = self.bombType

        # if no owner was provided, use an unconnected node ref
        if owner is None:
            owner = bs.Node(None)

        # the node this came from
        self.owner = owner

        # adding footing-materials to things can screw up jumping and flying since players carrying those things
        # and thus touching footing objects will think they're on solid ground..
        # perhaps we don't wanna add this even in the tnt case?..
        if self.bombType == 'tnt':
            materials = (factory.bombMaterial,
                         bs.getSharedObject('footingMaterial'),
                         bs.getSharedObject('objectMaterial'))
        else:
            materials = (factory.bombMaterial,
                         bs.getSharedObject('objectMaterial'))

        if self.bombType == 'impact' or self.bombType == 'curseBomb' or self.bombType == 'forceBomb':
            materials = materials + (factory.impactBlastMaterial, )

        elif self.bombType == 'landMine':
            materials = materials + (factory.landMineNoExplodeMaterial, )

        if self.bombType == 'sticky' or self.bombType == 'triggerBomb':
            materials = materials + (factory.stickyMaterial, )
        else:
            materials = materials + (factory.normalSoundMaterial, )

        if self.bombType == 'landMine':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={
                                       'position': position,
                                       'velocity': velocity,
                                       'model': factory.landMineModel,
                                       'lightModel': factory.landMineModel,
                                       'body': 'landMine',
                                       'shadowSize': 0.44,
                                       'colorTexture': factory.landMineTex,
                                       'reflection': 'powerup',
                                       'reflectionScale': [1.0],
                                       'materials': materials
                                   })

        elif self.bombType == 'tnt':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={
                                       'position': position,
                                       'velocity': velocity,
                                       'model': factory.tntModel,
                                       'lightModel': factory.tntModel,
                                       'body': 'sphere' if some.custom_tnt else 'crate',
                                       'shadowSize': 0.5,
                                       'colorTexture': factory.tntTex,
                                       'reflection': 'soft',
                                       'reflectionScale': [0.23],
                                       'materials': materials
                                   })

        elif self.bombType == 'curseBomb':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={
                                       'position': position,
                                       'velocity': velocity,
                                       'model': factory.curseBombModel,
                                       'body': 'sphere',
                                       'bodyScale': modelSize,
                                       'shadowSize': 0.5,
                                       'bodyScale': modelScale,
                                       'colorTexture': factory.curseBombTex,
                                       'reflection': 'soft',
                                       'reflectionScale': [0.4],
                                       'materials': materials
                                   })

        elif self.bombType == 'forceBomb':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   owner=owner,
                                   attrs={
                                       'position': position,
                                       'velocity': velocity,
                                       'model': factory.stickyBombModel,
                                       'lightModel': factory.stickyBombModel,
                                       'body': 'sphere',
                                       'bodyScale': modelSize,
                                       'shadowSize': 0.44,
                                       'colorTexture': factory.forceTex,
                                       'reflection': 'powerup',
                                       'reflectionScale': [1.0],
                                       'materials': materials
                                   })

        elif self.bombType == 'triggerBomb':
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   owner=owner,
                                   attrs={
                                       'position': position,
                                       'velocity': velocity,
                                       'model': factory.stickyBombModel,
                                       'lightModel': factory.stickyBombModel,
                                       'body': 'sphere',
                                       'shadowSize': 0.44,
                                       'colorTexture': factory.triggerBombTex,
                                       'reflection': 'powerup',
                                       'reflectionScale': [1.0],
                                       'sticky': True,
                                       'materials': materials
                                   })
            modelScale = 0.75
            self.sourcePlayer.actor.triggerBombs.append(self)

        elif self.bombType == 'impact':
            fuseTime = 20000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={
                                       'position': position,
                                       'velocity': velocity,
                                       'body': 'sphere',
                                       'model': factory.impactBombModel,
                                       'shadowSize': 0.3,
                                       'colorTexture': factory.impactTex,
                                       'reflection': 'powerup',
                                       'reflectionScale': [1.5],
                                       'materials': materials
                                   })
            self.armTimer = bs.Timer(
                200, bs.WeakCall(self.handleMessage, ArmMessage()))
            self.warnTimer = bs.Timer(
                fuseTime - 1700, bs.WeakCall(self.handleMessage,
                                             WarnMessage()))

        else:
            fuseTime = fuseTime
            if self.bombType == 'sticky':
                sticky = True
                model = factory.stickyBombModel
                rType = 'sharper'
                rScale = 1.8
            else:
                sticky = False
                model = factory.bombModel
                rType = 'sharper'
                rScale = 1.8
            if self.bombType == 'ice':
                tex = factory.iceTex
            elif self.bombType == 'sticky':
                tex = factory.stickyTex
            elif self.bombType == "cluster":
                tex = factory.clusterBombTex
            else:
                tex = factory.regularTex
            self.node = bs.newNode('bomb',
                                   delegate=self,
                                   attrs={
                                       'position': position,
                                       'velocity': velocity,
                                       'model': model,
                                       'shadowSize': 0.3,
                                       'colorTexture': tex,
                                       'sticky': sticky,
                                       'owner': owner,
                                       'reflection': rType,
                                       'reflectionScale': [rScale],
                                       'materials': materials
                                   })

            sound = bs.newNode('sound',
                               owner=self.node,
                               attrs={
                                   'sound': factory.fuseSound,
                                   'volume': 0.25
                               })
            self.node.connectAttr('position', sound, 'position')
            bsUtils.animate(self.node, 'fuseLength', {0: 1, fuseTime: 0})

        # light the fuse!!!
        if self.bombType not in ('landMine', 'tnt', 'curseBomb', "forceBomb",
                                 "triggerBomb"):
            bs.gameTimer(fuseTime,
                         bs.WeakCall(self.handleMessage, ExplodeMessage()))

        bsUtils.animate(self.node, "modelScale", {
            0: 0,
            200: 1.3,
            260: modelScale
        })

        self.blastBuffed = False

        def buffedSparks():
            if self.node.exists() and self.bombType not in [
                    'forceBomb', 'tnt', 'impact', 'curseBomb'
            ]:
                bs.emitBGDynamics(position=(self.node.position[0],
                                            self.node.position[1],
                                            self.node.position[2]),
                                  velocity=self.node.velocity,
                                  count=random.randrange(3, 5),
                                  scale=0.4,
                                  spread=0.1,
                                  chunkType='spark')
                bs.gameTimer(10, bs.Call(buffedSparks))
                self.blastBuffed = True
            else:
                self.blastBuffed = False

        if some.extra_sparkles: bs.gameTimer(400, bs.Call(buffedSparks))

    def getSourcePlayer(self):
        """
        Returns a bs.Player representing the source of this bomb.
        """
        if self.sourcePlayer is None:
            return bs.Player(None)  # empty player ref
        return self.sourcePlayer

    @classmethod
    def getFactory(cls):
        """
        Returns a shared bs.BombFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        try:
            return activity._sharedBombFactory
        except Exception:
            f = activity._sharedBombFactory = NewBombFactory()
            return f

    def onFinalize(self):
        bs.Actor.onFinalize(self)
        # release callbacks/refs so we don't wind up with dependency loops..
        self._explodeCallbacks = []

    def _handleDie(self, m):
        try:
            if self.bombType == 'triggerBomb':
                if self in self.sourcePlayer.actor.triggerBombs:
                    self.sourcePlayer.actor.triggerBombs.remove(self)
        except:
            pass
        self.node.delete()

    def _handleOOB(self, m):
        self.handleMessage(bs.DieMessage())

    def _handleImpact(self, m):
        node, body = bs.getCollisionInfo("opposingNode", "opposingBody")
        # if we're an impact bomb and we came from this node, don't explode...
        # alternately if we're hitting another impact-bomb from the same source, don't explode...
        try:
            nodeDelegate = node.getDelegate()
        except Exception:
            nodeDelegate = None
        if node is not None and node.exists():
            if (self.bombType == 'impact' and
                (node is self.owner or
                 (isinstance(nodeDelegate, Bomb) and nodeDelegate.bombType
                  == 'impact' and nodeDelegate.owner is self.owner))):
                return
            else:
                self.handleMessage(ExplodeMessage())

    def _handleForceBomb(self, m):
        node = bs.getCollisionInfo("opposingNode")
        if self.node.exists():
            if node is not self.owner and bs.getSharedObject(
                    'playerMaterial') in node.materials:
                self.node.sticky = True

                def on():
                    try:
                        self.node.extraAcceleration = (0, 160, 0)
                        if self.aim is not None:
                            self.aim.off()
                    except:
                        pass

                bs.gameTimer(2, on)

    def _handlecurseBomb(self, m):
        node, body = bs.getCollisionInfo("opposingNode", "opposingBody")
        # if we're an impact bomb and we came from this node, don't explode...
        # alternately if we're hitting another impact-bomb from the same source, don't explode...
        try:
            nodeDelegate = node.getDelegate()
        except Exception:
            nodeDelegate = None
        if node is not None and node.exists():
            if (self.bombType == 'curseBomb' and
                (node is self.owner or
                 (isinstance(nodeDelegate, Bomb) and nodeDelegate.bombType
                  == 'curseBomb' and nodeDelegate.owner is self.owner))):
                return
            else:
                self.handleMessage(ExplodeMessage())

    def _handleDropped(self, m):
        try:
            if self.sourcePlayer.actor.autoaim:

                def autoaim():
                    self.aim = portalObjects.AutoAim(self.node, self.owner)
                    bs.gameTimer(300, self.aim.off)

                bs.gameTimer(100, autoaim)
        except:
            pass

        if self.bombType == 'landMine':
            self.armTimer = bs.Timer(
                1250, bs.WeakCall(self.handleMessage, ArmMessage()))
        elif self.bombType == 'forceBomb':
            self.armTimer = bs.Timer(
                250, bs.WeakCall(self.handleMessage, ArmMessage()))

        # once we've thrown a sticky bomb we can stick to it..
        elif self.bombType == 'sticky':

            def _safeSetAttr(node, attr, value):
                if node.exists():
                    setattr(node, attr, value)

            # bs.gameTimer(250,bs.Call(_safeSetAttr,self.node,'stickToOwner',True))
            bs.gameTimer(250,
                         lambda: _safeSetAttr(self.node, 'stickToOwner', True))

    def _handleSplat(self, m):
        node = bs.getCollisionInfo("opposingNode")
        if node is not self.owner and bs.getGameTime(
        ) - self._lastStickySoundTime > 1000:
            self._lastStickySoundTime = bs.getGameTime()
            bs.playSound(self.getFactory().stickyImpactSound,
                         2.0,
                         position=self.node.position)

    def addExplodeCallback(self, call):
        """
        Add a call to be run when the bomb has exploded.
        The bomb and the new blast object are passed as arguments.
        """
        self._explodeCallbacks.append(call)

    def explode(self):
        """
        Blows up the bomb if it has not yet done so.
        """
        if self._exploded:
            return
        self._exploded = True
        activity = self.getActivity()
        if self.blastBuffed:
            try:
                self.lightExplode = bs.newNode('light',
                                               attrs={
                                                   'position':
                                                   self.node.position,
                                                   'color': (1.0, 1.0, 0.2),
                                                   'volumeIntensityScale': 0.5
                                               })
                bs.animate(self.lightExplode,
                           'intensity', {
                               0: 0,
                               100: self.blastRadius / 2,
                               500: 0
                           },
                           loop=False)
                bs.gameTimer(500, self.lightExplode.delete)
            except AttributeError:
                pass
        if not self.bombType in ['curseBomb']:
            if activity is not None and self.node.exists():
                if self.bombType == "cluster" and self.node.exists(
                ) and hasattr(self.node, "position"):

                    def _throwSubBombs(pos,
                                       vel,
                                       times,
                                       type,
                                       sourcePlayer,
                                       blastRadius=1.5,
                                       modelScale=0.5):
                        for index in range(times):
                            bs.Bomb(
                                position=pos,
                                velocity=tuple([
                                    item +
                                    random.uniform(-20, 20) * random.random()
                                    for item in vel
                                ]),
                                bombType=random.choice(type),
                                sourcePlayer=sourcePlayer,
                                blastRadius=blastRadius,
                                fuseTime=1000,
                                modelScale=modelScale).autoRetain()

                    bs.gameTimer(
                        50,
                        bs.Call(
                            _throwSubBombs, self.node.position,
                            self.node.velocity,
                            int(
                                random.randint(1, 4) *
                                pow(self.node.modelScale, 3)),
                            ['normal', 'ice', 'cluster'], self.sourcePlayer,
                            self.blastRadius, 0.7))
                blast = Blast(position=self.node.position,
                              velocity=self.node.velocity,
                              blastRadius=self.blastRadius,
                              blastType=self.bombType,
                              sourcePlayer=self.sourcePlayer,
                              hitType=self.hitType,
                              hitSubType=self.hitSubType).autoRetain()
                for c in self._explodeCallbacks:
                    c(self, blast)
                if self.bombType == 'landMine':
                    if bs.getSharedObject('globals').slowMotion == False:

                        def slowMo():
                            bs.getSharedObject(
                                'globals').slowMotion = bs.getSharedObject(
                                    'globals').slowMotion == False

                        #slowMo()
                        #bs.playSound(bs.getSound("orchestraHitBig2"))
                        #bs.gameTimer(600, bs.Call(slowMo))

        elif self.bombType == 'curseBomb':
            import portalObjects
            portalObjects.Poison(position=self.node.position)
            bs.playSound(self.getFactory().curseBombSound,
                         position=self.node.position)

        # we blew up so we need to go away
        bs.gameTimer(1, bs.WeakCall(self.handleMessage, bs.DieMessage()))

    def _handleWarn(self, m):
        try:
            if self.textureSequence.exists():
                self.textureSequence.rate = 30
                bs.playSound(self.getFactory().warnSound,
                             0.5,
                             position=self.node.position)
        except:
            pass

    def _addMaterial(self, material):
        if not self.node.exists():
            return
        materials = self.node.materials
        if not material in materials:
            self.node.materials = materials + (material, )

    def arm(self):
        """
        Arms land-mines and impact-bombs so
        that they will explode on impact.
        """
        if not self.node.exists():
            return
        factory = self.getFactory()
        if self.bombType == 'landMine':
            self.textureSequence = bs.newNode('textureSequence',
                                              owner=self.node,
                                              attrs={
                                                  'inputTextures':
                                                  (factory.landMineLitTex,
                                                   factory.landMineTex),
                                                  'rate':
                                                  30
                                              })
            bs.gameTimer(500, self.textureSequence.delete)
            # we now make it explodable.
            bs.gameTimer(
                250,
                bs.WeakCall(self._addMaterial, factory.landMineBlastMaterial))
        elif self.bombType == 'forceBomb':
            # self.setSticky()
            bs.playSound(bs.getSound('activateBeep'),
                         position=self.node.position)
            self.aim = portalObjects.AutoAim(self.node, self.owner)
            bs.gameTimer(2500, self.node.delete)

        elif self.bombType == 'impact':
            self.textureSequence = bs.newNode('textureSequence',
                                              owner=self.node,
                                              attrs={
                                                  'inputTextures':
                                                  (factory.impactLitTex,
                                                   factory.impactTex,
                                                   factory.impactTex),
                                                  'rate':
                                                  100
                                              })
            bs.gameTimer(
                250,
                bs.WeakCall(self._addMaterial, factory.landMineBlastMaterial))
        else:
            raise Exception(
                'arm() should only be called on land-mines or impact bombs')
        if not self.bombType in ['forceBomb', 'slipper']:
            self.textureSequence.connectAttr('outputTexture', self.node,
                                             'colorTexture')
            bs.playSound(factory.activateSound,
                         0.5,
                         position=self.node.position)

    def _handleHit(self, m):
        isPunch = (m.srcNode.exists() and m.srcNode.getNodeType() == 'spaz')

        # normal bombs are triggered by non-punch impacts..  impact-bombs by all impacts
        if not self._exploded and not isPunch or self.bombType in [
                'impact', 'landMine'
        ]:
            # also lets change the owner of the bomb to whoever is setting us off..
            # (this way points for big chain reactions go to the person causing them)
            if m.sourcePlayer not in [None]:
                self.sourcePlayer = m.sourcePlayer

                # also inherit the hit type (if a landmine sets off by a bomb, the credit should go to the mine)
                # the exception is TNT.  TNT always gets credit.
                if self.bombType != 'tnt':
                    self.hitType = m.hitType
                    self.hitSubType = m.hitSubType

            bs.gameTimer(100 + int(random.random() * 100),
                         bs.WeakCall(self.handleMessage, ExplodeMessage()))
        self.node.handleMessage("impulse", m.pos[0], m.pos[1], m.pos[2],
                                m.velocity[0], m.velocity[1], m.velocity[2],
                                m.magnitude, m.velocityMagnitude, m.radius, 0,
                                m.velocity[0], m.velocity[1], m.velocity[2])

        if m.srcNode.exists():
            pass
            #print 'FIXME HANDLE KICKBACK ON BOMB IMPACT'
            # bs.nodeMessage(m.srcNode,"impulse",m.srcBody,m.pos[0],m.pos[1],m.pos[2],
            #                     -0.5*m.force[0],-0.75*m.force[1],-0.5*m.force[2])

    def handleMessage(self, m):
        if isinstance(m, ExplodeMessage):
            self.explode()
        elif isinstance(m, ImpactMessage):
            if not self.bombType in ['curseBomb', 'forceBomb']:
                self._handleImpact(m)
            elif self.bombType == 'forceBomb':
                self._handleForceBomb(m)
            elif self.bombType == 'curseBomb':
                self._handlecurseBomb(m)
        elif isinstance(m, bs.PickedUpMessage):
            # change our source to whoever just picked us up *only* if its None
            # this way we can get points for killing bots with their own bombs
            # hmm would there be a downside to this?...
            if self.sourcePlayer is not None:
                self.sourcePlayer = m.node.sourcePlayer
        elif isinstance(m, SplatMessage):
            self._handleSplat(m)
        elif isinstance(m, bs.DroppedMessage):
            self._handleDropped(m)
        elif isinstance(m, bs.HitMessage):
            self._handleHit(m)
        elif isinstance(m, bs.DieMessage):
            self._handleDie(m)
        elif isinstance(m, bs.OutOfBoundsMessage):
            self._handleOOB(m)
        elif isinstance(m, ArmMessage):
            self.arm()
        elif isinstance(m, WarnMessage):
            self._handleWarn(m)
        else:
            bs.Actor.handleMessage(self, m)


bsBomb.Bomb = NewBomb
bsBomb.BombFactory = NewBombFactory
bs.BombFactory = NewBombFactory
bs.Bomb = NewBomb
bsBomb.Blast.__init__ = __init__
