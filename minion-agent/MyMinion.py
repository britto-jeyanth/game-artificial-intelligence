'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from moba import *

class MyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###
		self.states.append(MoveToTower)
		self.states.append(MoveToBase)
		self.states.append(AttackBase)
		self.states.append(AttackTower)
		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(Idle)





############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		team1 = self.agent.getTeam()
		team2Towers = self.agent.world.getEnemyTowers(team1)
		team2Bases = self.agent.world.getEnemyBases(team1)

		if(len(team2Towers)>0):
			self.agent.changeState(MoveToTower)
		elif(len(team2Bases)>0):
			self.agent.changeState(MoveToBase)
		else:
			self.agent.stopMoving()
		### YOUR CODE GOES ABOVE HERE ###
		return None

##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		if self.victim is not None:
			print "Hey " + str(self.victim) + ", I don't like you!"
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:

class MoveToTower(State):

	def enter(self, delta = 0):
		team1 = self.agent.getTeam()
		enemyTowers = self.agent.world.getEnemyTowers(team1)
		minPos = self.agent.getLocation()

		closestTower = ''
		minDist = 0

		for tower in enemyTowers:
			dist1 = distance(minPos, tower.getLocation())
			if minDist == 0:
				minDist = dist1
				closestTower = tower
			elif dist1<minDist:
				minDist = dist1
				closestTower=tower
		if(len(enemyTowers)>0):
			self.agent.navigateTo(closestTower.getLocation())

	def execute(self, delta):
		team1 = self.agent.getTeam()
		team2Towers = self.agent.world.getEnemyTowers(team1)
		team2Bases = self.agent.world.getEnemyBases(team1)
		minPos = self.agent.getLocation()

		closestTower = ''
		minDist = 0

		if(len(team2Towers)>0):
			for tower in team2Towers:
				dist1 = distance(minPos, tower.getLocation())
				if minDist == 0:
					minDist = dist1
					closestTower = tower
				elif dist1 < minDist:
					minDist = dist1
					closestTower = tower

		if len(team2Towers) > 0 and (not self.agent.isMoving()):
			self.agent.navigateTo(closestTower.getLocation())

		if(len(team2Towers) > 0 and minDist<150):
			self.agent.changeState(AttackTower)

		closestBase = ''
		minBDist = 0
		if(len(team2Bases)>0 and len(team2Towers)==0):
			for base in team2Bases:
				dist1 = distance(minPos, base.getLocation())
				if minBDist == 0:
					minBDist = dist1
					closestBase = base
				elif dist1 < minDist:
					minBDist = dist1
					closestBase = base

			if minBDist>150:
				self.agent.changeState(MoveToBase)

			elif minBDist>0 and minBDist<150:
				self.agent.changeState(AttackBase)


		### YOUR CODE GOES ABOVE HERE ###
		return None

class AttackTower(State):

	def enter(self, oldstate):
		self.agent.stopMoving()
		team1 = self.agent.getTeam()
		enemyTowers = self.agent.world.getEnemyTowers(team1)
		minPos = self.agent.getLocation()
		closestTower = ''
		minDist = 0

		for tower in enemyTowers:
			dist1 = distance(minPos, tower.getLocation())
			if minDist == 0:
				minDist = dist1
				closestTower = tower
			elif dist1 < minDist:
				minDist = dist1
				closestTower = tower

		if(len(enemyTowers)>0):
			self.target = closestTower

	def execute(self, delta = 0):
		team1 = self.agent.getTeam()
		enemyTowers = self.agent.world.getEnemyTowers(team1)
		minPos = self.agent.getLocation()
		closestTower = ''
		minDist = 0

		for tower in enemyTowers:
			dist1 = distance(minPos, tower.getLocation())
			if minDist == 0:
				minDist = dist1
				closestTower = tower
			elif dist1 < minDist:
				minDist = dist1
				closestTower = tower
		if (len(enemyTowers) > 0 and minDist>0):
			self.agent.turnToFace(closestTower.getLocation())
			self.agent.shoot()


			if(self.target.isAlive()):
				self.agent.changeState(AttackTower)
			else:
				enemyTowers = self.agent.world.getEnemyTowers(team1)
				if(len(enemyTowers)>0):
					self.agent.changeState(MoveToTower)
				else:
					self.agent.changeState(MoveToBase)
		else:
			self.agent.changeState(MoveToBase)

class MoveToBase(State):

	def enter(self, delta = 0):
		team1 = self.agent.getTeam()
		enemyBases = self.agent.world.getEnemyBases(team1)
		minPos = self.agent.getLocation()

		closestBase = ''
		minDist = 0

		for base in enemyBases:
			dist1 = distance(minPos, base.getLocation())
			if minDist == 0:
				minDist = dist1
				closestBase = base
			elif dist1<minDist:
				minDist = dist1
				closestBase=base
		if len(enemyBases)>0:
			self.agent.navigateTo(closestBase.getLocation())

	def execute(self, delta):
		team1 = self.agent.getTeam()
		team2Bases = self.agent.world.getEnemyBases(team1)
		minPos = self.agent.getLocation()


		closestBase = ''
		minBDist = 0
		if(len(team2Bases)>0):
			for base in team2Bases:
				dist1 = distance(minPos, base.getLocation())
				if minBDist == 0:
					minBDist = dist1
					closestBase = base
				elif dist1 < minDist:
					minBDist = dist1
					closestBase = base

			if minBDist>150 and (not self.agent.isMoving()):
				self.agent.navigateTo(closestBase.getLocation())

			if minBDist>0 and minBDist<150:
				self.agent.changeState(AttackBase)


		### YOUR CODE GOES ABOVE HERE ###
		return None

class AttackBase(State):

	def enter(self, oldstate):
		self.agent.stop()

	def execute(self, delta = 0):
		team1 = self.agent.getTeam()
		enemyBases = self.agent.world.getEnemyBases(team1)
		minPos = self.agent.getLocation()

		closestBase = ''
		minDist = 0

		for base in enemyBases:
			dist1 = distance(minPos, base.getLocation())
			if minDist == 0:
				minDist = dist1
				closestBase = base
			elif dist1 < minDist:
				minDist = dist1
				closestBase = base
		if minDist>0 and len(enemyBases)>0:
			self.agent.turnToFace(closestBase.getLocation())
			self.agent.shoot()
		else:
			self.agent.changeState(MoveToBase)

