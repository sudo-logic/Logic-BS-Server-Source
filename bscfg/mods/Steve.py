# coding=utf-8
from bsSpaz import Appearance

###############  SPAZ   ##################
t = Appearance("Steve")

t.colorTexture = u"cowboyColor"
t.colorMaskTexture = u"cowboyColorMask"

t.iconTexture = u"cowboyIcon"
t.iconMaskTexture = u"cowboyIconColorMask"

t.defaultColor = (0.75, 0.75, 0.75)
t.defaultHighlight = (0.5, 0.5, 0.5)

t.headModel = "cowboyHead"
t.torsoModel = "cowboyTorso"
t.pelvisModel = "cowboyPelvis"
t.upperArmModel = "cowboyUpperArm"
t.foreArmModel = "cowboyForeArm"
t.handModel = "cowboyHand"
t.upperLegModel = "cowboyUpperLeg"
t.lowerLegModel = "cowboyLowerLeg"
t.toesModel = "cowboyToes"

t.jumpSounds = [
    "kronk1", "kronk2", "kronk3", "kronk4", "kronk5", "kronk6", "kronk7",
    "kronk8", "kronk9", "kronk10"
]
t.attackSounds = [
    "kronk1", "kronk2", "kronk3", "kronk4", "kronk5", "kronk6", "kronk7",
    "kronk8", "kronk9", "kronk10"
]
t.impactSounds = [
    "kronk1", "kronk2", "kronk3", "kronk4", "kronk5", "kronk6", "kronk7",
    "kronk8", "kronk9", "kronk10"
]
t.deathSounds = ["kronkDeath"]
t.pickupSounds = [
    "kronk1", "kronk2", "kronk3", "kronk4", "kronk5", "kronk6", "kronk7",
    "kronk8", "kronk9", "kronk10"
]
t.fallSounds = ["kronkFall"]

t.style = 'agent'
