import bsPowerup
from bsPowerup import *
import bs
import some

from bsPowerup import PowerupMessage, PowerupAcceptMessage, _TouchedMessage, PowerupFactory, Powerup


class _TouchedMessage(object):
    pass


class PowerupFactory(object):
    """
    category: Game Flow Classes

    Wraps up media and other resources used by bs.Powerups.
    A single instance of this is shared between all powerups
    and can be retrieved via bs.Powerup.getFactory().

    Attributes:

       model
          The bs.Model of the powerup box.

       modelSimple
          A simpler bs.Model of the powerup box, for use in shadows, etc.

       texBox
          Triple-bomb powerup bs.Texture.

       texPunch
          Punch powerup bs.Texture.

       texIceBombs
          Ice bomb powerup bs.Texture.

       texStickyBombs
          Sticky bomb powerup bs.Texture.

       texShield
          Shield powerup bs.Texture.

       texImpactBombs
          Impact-bomb powerup bs.Texture.

       texHealth
          Health powerup bs.Texture.

       texLandMines
          Land-mine powerup bs.Texture.

       texCurse
          Curse powerup bs.Texture.

       healthPowerupSound
          bs.Sound played when a health powerup is accepted.

       powerupSound
          bs.Sound played when a powerup is accepted.

       powerdownSound
          bs.Sound that can be used when powerups wear off.

       powerupMaterial
          bs.Material applied to powerup boxes.

       powerupAcceptMaterial
          Powerups will send a bs.PowerupMessage to anything they touch
          that has this bs.Material applied.
    """
    def __init__(self):
        """
        Instantiate a PowerupFactory.
        You shouldn't need to do this; call bs.Powerup.getFactory() to get a shared instance.
        """

        self._lastPowerupType = None

        self.model = bs.getModel("powerup")
        self.modelSimple = bs.getModel("powerupSimple")

        self.texBomb = bs.getTexture("powerupBomb")
        self.texPunch = bs.getTexture("powerupPunch")
        self.texIceBombs = bs.getTexture("powerupIceBombs")
        self.texStickyBombs = bs.getTexture("powerupStickyBombs")
        self.texShield = bs.getTexture("powerupShield")
        self.texImpactBombs = bs.getTexture("powerupImpactBombs")
        self.texPortal = bs.getTexture("coin")
        self.texRainbow = bs.getTexture("achievementFlawlessVictory")
        self.texHealth = bs.getTexture("powerupHealth")
        self.texLandMines = bs.getTexture("powerupLandMines")
        self.texcurseBomb = bs.getTexture("powerupCurse")
        self.texHeatSeeker = bs.getTexture("landMineLit")
        self.texQuake = bs.getTexture("levelIcon")
        self.texCurse = random.choice(
            (bs.getTexture("powerupHealth"), bs.getTexture("powerupShield")))
        self.texDroneStrike = bs.getTexture("sparks")
        self.texAim = bs.getTexture("ouyaAButton")
        self.texBubblePower = bs.getTexture("light")
        self.texTriggerBombs = bs.getTexture("egg4")
        self.texClusterBombs = bs.getTexture("menuIcon")

        self.healthPowerupSound = bs.getSound("healthPowerup")
        self.powerupSound = bs.getSound("powerup01")
        self.powerdownSound = bs.getSound("powerdown01")
        self.dropSound = bs.getSound("boxDrop")

        # material for powerups
        self.powerupMaterial = bs.Material()

        # material for anyone wanting to accept powerups
        self.powerupAcceptMaterial = bs.Material()

        # pass a powerup-touched message to applicable stuff
        self.powerupMaterial.addActions(
            conditions=(("theyHaveMaterial", self.powerupAcceptMaterial)),
            actions=(("modifyPartCollision", "collide",
                      True), ("modifyPartCollision", "physical", False),
                     ("message", "ourNode", "atConnect", _TouchedMessage())))

        # we dont wanna be picked up
        if not some.interactive_powerups:
            self.powerupMaterial.addActions(
              conditions=("theyHaveMaterial",bs.getSharedObject('pickupMaterial')),
              actions=( ("modifyPartCollision","collide",False)))

        self.powerupMaterial.addActions(
            conditions=("theyHaveMaterial",
                        bs.getSharedObject('footingMaterial')),
            actions=(("impactSound", self.dropSound, 0.5, 0.1)))

        self._powerupDist = []
        for p, freq in getDefaultPowerupDistribution():
            for i in range(int(freq)):
                self._powerupDist.append(p)

    def getRandomPowerupType(self, forceType=None, excludeTypes=[]):
        """
        Returns a random powerup type (string).
        See bs.Powerup.powerupType for available type values.

        There are certain non-random aspects to this; a 'curse' powerup, for instance,
        is always followed by a 'health' powerup (to keep things interesting).
        Passing 'forceType' forces a given returned type while still properly interacting
        with the non-random aspects of the system (ie: forcing a 'curse' powerup will result
        in the next powerup being health).
        """
        if forceType:
            t = forceType
        else:
            # if the last one was a curse, make this one a health to provide some hope
            if self._lastPowerupType == 'curse':
                t = 'health'

            else:
                while True:
                    t = self._powerupDist[random.randint(
                        0,
                        len(self._powerupDist) - 1)]
                    if t not in excludeTypes:
                        break
        self._lastPowerupType = t
        return t


def getDefaultPowerupDistribution():
    if some.modded_powerups:
        return some.powerup_dist
    else:
        return (('tripleBombs', 3), ('iceBombs', 3), ('punch', 3),
                ('impactBombs', 3), ('landMines', 2), ('stickyBombs', 3),
                ('shield', 2), ('health', 1), ('curse', 1))
    # return (('tripleBombs',0),
    #         ('iceBombs',0),
    #         ('punch',0),
    #         ('impactBombs',0),
    #         ('landMines',0),
    #         ('stickyBombs',0),
    #         ('shield',0),
    #         ('health',0),
    #         ('curseBomb',0),
    #         ('portal',0),
    #         ('invisible',0),
    #         ('curse',0))


class Powerup(bs.Actor):
    """
    category: Game Flow Classes

    A powerup box.
    This will deliver a bs.PowerupMessage to anything that touches it
    which has the bs.PowerupFactory.powerupAcceptMaterial applied.

    Attributes:

       powerupType
          The string powerup type.  This can be 'tripleBombs', 'punch',
          'iceBombs', 'impactBombs', 'landMines', 'stickyBombs', 'shield',
          'health', or 'curse'.

       node
          The 'prop' bs.Node representing this box.
    """
    def __init__(self,
                 position=(0, 1, 0),
                 velocity=(0, 0, 0),
                 powerupType='tripleBombs',
                 expire=True,
                 small=False):
        """
        Create a powerup-box of the requested type at the requested position.

        see bs.Powerup.powerupType for valid type strings.
        """

        bs.Actor.__init__(self)

        factory = self.getFactory()
        self.powerupType = powerupType
        self._powersGiven = False

        mod = factory.model
        mScl = 1
        color = (1, 1, 1)

        if powerupType == 'tripleBombs':
            tex = factory.texBomb
        elif powerupType == 'punch':
            tex = factory.texPunch
        elif powerupType == 'iceBombs':
            tex = factory.texIceBombs
        elif powerupType == 'impactBombs':
            tex = factory.texImpactBombs
        elif powerupType == 'landMines':
            tex = factory.texLandMines
        elif powerupType == 'curseBomb':
            tex = factory.texcurseBomb
        elif powerupType == 'stickyBombs':
            tex = factory.texStickyBombs
        elif powerupType == 'heatSeeker':
            tex = factory.texHeatSeeker
        elif powerupType == 'droneStrike':
            tex = factory.texDroneStrike
        elif powerupType == 'shield':
            tex = factory.texShield
        elif powerupType == 'invisible':
            tex = factory.texRainbow
        elif powerupType == 'portal':
            tex = factory.texPortal
        elif powerupType == 'health':
            tex = factory.texHealth
        elif powerupType == 'curse':
            tex = factory.texCurse
        elif powerupType == 'trailblazer':
            tex = factory.texQuake
        elif powerupType == 'autoaim':
            tex = factory.texAim
        elif powerupType == "clusterBombs":
            tex = factory.texClusterBombs
        elif powerupType == "bubblePower":
            tex = factory.texBubblePower
        elif powerupType == "triggerBombs":
            tex = factory.texTriggerBombs
        else:
            raise Exception("invalid powerupType: " + str(powerupType))

        if len(position) != 3:
            raise Exception("expected 3 floats for position")

        self.node = bs.newNode(
            'prop',
            delegate=self,
            attrs={
                'body':
                'box',
                'position': [position[0], position[1], position[2]],
                'model':
                mod,
                'velocity':
                velocity,
                'lightModel':
                mod,
                'shadowSize':
                0.5,
                'colorTexture':
                tex,
                'reflection':
                'powerup',
                # 'reflectionScale':[0.65], # this white spot covered my masterpiece textures!
                'materials':
                (factory.powerupMaterial, bs.getSharedObject('objectMaterial'))
            })

        # animate in..
        self.picked = False
        curve = bs.animate(self.node, "modelScale", {
            0: 0,
            140: 0.7 if small else 1.6,
            200: 0.6 if small else 1
        })
        bs.gameTimer(200, curve.delete)

        m = bs.newNode('math',
                           owner=self.node,
                           attrs={
                               'input1': (0, 0.7, 0),
                               'operation': 'add'
                           })
        self.node.connectAttr('position', m, 'input2')
        if some.show_powerup_name:
            self._powText = bs.newNode('text',
                                       owner=self.node,
                                       attrs={
                                           'text': powerupType.upper(),
                                           'inWorld': True,
                                           'shadow': 1.0,
                                           'flatness': 1.0,
                                           'color': (1, 1, 1),
                                           'scale': 0.01,
                                           'hAlign': 'center'
                                       })
            m.connectAttr('output', self._powText, 'position')

        if some.night:
            self.nodeLight = bs.newNode('light',
                                            owner=self.node,
                                            attrs={
                                                'position': self.node.position,
                                                'color': (0.5, 0.5, 0.5),
                                                'radius': 0.5,
                                                'intensity': 0.5,
                                                'volumeIntensityScale': 1.0
                                            })
            self.node.connectAttr('position', self.nodeLight, 'position')

        if expire:
            bs.gameTimer(defaultPowerupInterval - 2500,
                         bs.WeakCall(self._startFlashing))
            bs.gameTimer(defaultPowerupInterval - 1000,
                         bs.WeakCall(self.handleMessage, bs.DieMessage()))

    @classmethod
    def getFactory(cls):
        """
        Returns a shared bs.PowerupFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        if activity is None:
            raise Exception("no current activity")
        try:
            return activity._sharedPowerupFactory
        except Exception:
            f = activity._sharedPowerupFactory = PowerupFactory()
            return f

    def _startFlashing(self):
        if self.node.exists():
            self.node.flashing = True

    def handleMessage(self, m):
        self._handleMessageSanityCheck()

        if isinstance(m, PowerupAcceptMessage):
            factory = self.getFactory()
            if self.powerupType == 'health':
                bs.playSound(factory.healthPowerupSound,
                             3,
                             position=self.node.position)
            bs.playSound(factory.powerupSound, 3, position=self.node.position)
            self._powersGiven = True
            self.handleMessage(bs.DieMessage())

        elif isinstance(m, _TouchedMessage):
            if not self._powersGiven and not self.picked:
                node = bs.getCollisionInfo("opposingNode")
                if node is not None and node.exists():
                    node.handleMessage(
                        PowerupMessage(self.powerupType, sourceNode=self.node))

        elif isinstance(m, bs.DieMessage):
            if self.node.exists():
                if (m.immediate):
                    self.node.delete()
                else:
                    curve = bs.animate(self.node, "modelScale", {0: 1, 100: 0})
                    if some.show_powerup_name: curve1 = bs.animate(self._powText, "scale", {
                        0: 0.01,
                        100: 0
                    })
                    if hasattr(self, 'nodeLight'):
                        curve2 = bs.animate(self.nodeLight, "radius", {
                            0: 0.5,
                            100: 0
                        })
                    bs.gameTimer(100, self.node.delete)

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.PickedUpMessage):
            self.picked = True

        elif isinstance(m, bs.DroppedMessage):
            self.picked = False

        elif isinstance(m, bs.HitMessage):
            # dont die on punches (thats annoying)
            msg = m
            if some.interactive_powerups:
	            self.node.handleMessage("impulse", msg.pos[0], msg.pos[1],
	                                    msg.pos[2], msg.velocity[0],
	                                    msg.velocity[1], msg.velocity[2],
	                                    msg.magnitude, msg.velocityMagnitude,
	                                    msg.radius, 0, msg.velocity[0],
	                                    msg.velocity[1], msg.velocity[2])
            if m.hitType != 'punch':
                self.handleMessage(bs.DieMessage())
        else:
            bs.Actor.handleMessage(self, m)


bsPowerup.PowerupFactory = PowerupFactory
bsPowerup.Powerup = Powerup
bsPowerup.getDefaultPowerupDistribution = getDefaultPowerupDistribution
bsPowerup._TouchedMessage = _TouchedMessage
