# coding=utf-8
from bsSpaz import Appearance

###############  SPAZ   ##################
t = Appearance("Logicon")

t.colorTexture = "cyborgColor"
t.colorMaskTexture = "neoSpazColorMask"

t.defaultColor = (1, 0.5, 0)
t.defaultHighlight = (1, 1, 1)

t.iconTexture = "powerupCurse"
t.iconMaskTexture = "powerupCurseMask"

t.headModel = "cyborgHead"

t.torsoModel = "aliTorso"

t.pelvisModel = "aliPelvis"

t.upperArmModel = "aliUpperArm"
t.foreArmModel = "aliForeArm"
t.handModel = "aliHand"

t.upperLegModel = "aliUpperLeg"
t.lowerLegModel = "aliLowerLeg"
t.toesModel = "aliToes"

aliSounds = ['ali1', 'ali2', 'ali3', 'ali4']
aliHitSounds = ['aliHit1', 'aliHit2']

t.attackSounds = aliSounds
t.jumpSounds = aliSounds
t.impactSounds = aliHitSounds
t.deathSounds = ["aliDeath"]
t.pickupSounds = aliSounds
t.fallSounds = ["aliFall"]

t.style = 'ali'
