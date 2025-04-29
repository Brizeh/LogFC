# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 00:25:44 2025

@author: chauw
"""

class Joueur:

    def __init__(self,Name):
        super().__init__()
        self.name=Name
        self.boss_encounter   = []
        self.dps   = []
        self.cc   = []
        self.dps_supp   = []
        self.quick   = []
        self.alac   = []        
        self.mec_take   = []

        Joueur.last = self

Glyn=Joueur('Glyn')
print(Glyn.name)