# -*- coding: utf-8 -*-
import bsGame
import bsUtils
import bsInternal
import random
import bs
import some
from thread import start_new_thread
import bsScoreBoard
import weakref
import bsTeamGame
from bsTeamGame import *


def setup():
    bsTeamGame.gDefaultTeamColors = ((0.5, 1.0, 1.0), (1.0, 1.0, 0.5))
    bsTeamGame.gDefaultTeamNames = ("α Alpha Team α", "β Beta Team β")
    #if getattr(some,'four_teams',False):
    #   bsTeamGame.gDefaultTeamColors += ((1,0,0), (0, 1, 0))
    #  bsTeamGame.gDefaultTeamNames += ("y Gamma Team y", "ẟ Delta Team ẟ")


if some.logic_team_settings: setup()
