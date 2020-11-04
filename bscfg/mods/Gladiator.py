# coding=utf-8
from bsSpaz import Appearance

###############  SPAZ   ##################
t = Appearance("Raphael")

t.colorTexture = "warriorColor"
t.colorMaskTexture = "warriorColorMask"
# 主要制作:Plasma Boson 致谢:寂寥长空
t.iconTexture = "warriorIcon"
t.iconMaskTexture = "warriorIconColorMask"

t.defaultColor = (0.55, 0.55, 0.55)
t.defaultHighlight = (0.5, 0.5, 0.5)

t.headModel = "warriorHead"
t.torsoModel = "warriorTorso"
t.pelvisModel = "warriorPelvis"
t.upperArmModel = "warriorUpperArm"
t.foreArmModel = "warriorForeArm"
t.handModel = "warriorHand"
t.upperLegModel = "warriorUpperLeg"
t.lowerLegModel = "warriorLowerLeg"
t.toesModel = "warriorToes"

t.jumpSounds = ["warrior1", "warrior2", "warrior3"]
t.attackSounds = ["warrior1", "warrior2", "warrior3"]
t.impactSounds = [
    "warriorhit1",
    "warriorhit2",
]
t.deathSounds = ["warriorDeath", "warrior4"]
t.pickupSounds = ["warrior3"]
t.fallSounds = ["warriorDeath", "warrior4", "warriorFall"]

t.style = 'agent'
