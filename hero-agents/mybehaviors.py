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
from moba2 import *
from btnode import *

###########################
### SET UP BEHAVIOR TREE


def treeSpec(agent):
	myid = str(agent.getTeam())
	spec = None
	### YOUR CODE GOES BELOW HERE ###
	# spec = [
	#     (SuperRoot, agent, "root"),
	#     [
	#         (Selector, agent, "sel_1"),
	#         [
	#             (Retreat, agent, 0.5, "retreat"),
	#             (Selector, agent, "hero_minion_sel"),
	#             [
	#                 (BuffDaemon, agent, 1, "bf_daemon"),
	#                 [
	#                     (Sequence, agent, "hero_seq"),
	#                     [
	#                         (ChaseHero, agent, "chase_hero"),
	#                         (KillHero, agent, "kill_hero")
	#                     ]
	#                 ],
	#                 (BuffAndHPDaemon, agent, 3, "bfhp_daemon"),
	#                 [
	#                     (Sequence, agent, "hero_seq1"),
	#                     [
	#                         (ChaseHero, agent, "chase_hero1"),
	#                         (KillHero, agent, "kill_hero1")
	#                     ]
	#                 ],
	#                 (NoMoreThanNEnemiesDaemon, agent, 3, "no_more_than_3_enemies_daemon"),
	#                 [
	#                     (Sequence, agent, "minion_seq"),
	#                     [
	#                         (ChaseMinion, agent, "chase_minion"),
	#                         (KillMinion, agent, "kill_minion")
	#                     ]
	#                 ]
	#             ]
	#         ]
	#     ]
	# ]
	### YOUR CODE GOES ABOVE HERE ###
	return spec

def myBuildTree(agent):
	myid = str(agent.getTeam())
	root = None
	### YOUR CODE GOES BELOW HERE ###

	root = makeNode(ParentRoot, agent, "parent")
	selector_1 = makeNode(Selector, agent, "first selector")
	root.addChild(selector_1)

	retreat = makeNode(Retreat, agent, 0.5, "retreat")
	hp_daemon = makeNode(HitpointDaemon, agent, 0.4, "hit point check")
	selector_1.addChild(retreat)
	selector_1.addChild(hp_daemon)

	selector_2 = makeNode(Selector, agent, "second selector")
	hp_daemon.addChild(selector_2)

	bf_daemon = makeNode(BuffDaemon, agent, 2, "level limit check")
	bfhp_daemon = makeNode(BuffAndHPDaemon, agent, 3, "custom level and hp check")
	nomorenemies_daemon = makeNode(NoMoreThanNEnemiesDaemon, agent, 3, "no more than 3 enemies daemon")

	selector_2.addChild(bf_daemon)
	selector_2.addChild(bfhp_daemon)
	selector_2.addChild(nomorenemies_daemon)

	sequence_1 = makeNode(Sequence, agent, "sequence 1")
	bf_daemon.addChild(sequence_1)
	sequence_1.addChild(makeNode(ChaseHero, agent, "chase hero"))
	sequence_1.addChild(makeNode(KillHero, agent, "kill hero"))

	sequence_2 = makeNode(Sequence, agent, "sequence 2")
	bfhp_daemon.addChild(sequence_2)
	sequence_2.addChild(makeNode(ChaseHero, agent, "chase hero"))
	sequence_2.addChild(makeNode(KillHero, agent, "kill hero"))

	sequence_3 = makeNode(Sequence, agent, "sequence 3")
	nomorenemies_daemon.addChild(sequence_3)
	sequence_3.addChild(makeNode(ChaseMinion, agent, "chase minion"))
	sequence_3.addChild(makeNode(KillMinion, agent, "kill minion"))

	### YOUR CODE GOES ABOVE HERE ###
	return root

### Helper function for making BTNodes (and sub-classes of BTNodes).
### type: class type (BTNode or a sub-class)
### agent: reference to the agent to be controlled
### This function takes any number of additional arguments that will be passed to the BTNode and parsed using BTNode.parseArgs()
def makeNode(type, agent, *args):
	node = type(agent, args)
	return node

###############################
### BEHAVIOR CLASSES:


##################
### Taunt
###
### Print disparaging comment, addressed to a given NPC
### Parameters:
###   0: reference to an NPC
###   1: node ID string (optional)

class Taunt(BTNode):

	### target: the enemy agent to taunt

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		# First argument is the target
		if len(args) > 0:
			self.target = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target is not None:
			print "Hey", self.target, "I don't like you!"
		return ret

##################
### MoveToTarget
###
### Move the agent to a given (x, y)
### Parameters:
###   0: a point (x, y)
###   1: node ID string (optional)

class MoveToTarget(BTNode):
	
	### target: a point (x, y)
	
	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		# First argument is the target
		if len(args) > 0:
			self.target = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def enter(self):
		BTNode.enter(self)
		self.agent.navigateTo(self.target)

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None:
			# failed executability conditions
			print "exec", self.id, "false"
			return False
		elif distance(self.agent.getLocation(), self.target) < self.agent.getRadius():
			# Execution succeeds
			print "exec", self.id, "true"
			return True
		else:
			# executing
			return None
		return ret

##################
### Retreat
###
### Move the agent back to the base to be healed
### Parameters:
###   0: percentage of hitpoints that must have been lost to retreat
###   1: node ID string (optional)


class Retreat(BTNode):
	
	### percentage: Percentage of hitpoints that must have been lost
	
	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.percentage = 0.5
		# First argument is the factor
		if len(args) > 0:
			self.percentage = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def enter(self):
		BTNode.enter(self)
		base = self.agent.world.getBaseForTeam(self.agent.getTeam())
		if base:
			self.agent.navigateTo(base.getLocation())
	
	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.agent.getHitpoints() > self.agent.getMaxHitpoints() * self.percentage:
			# fail executability conditions
			print "exec", self.id, "false"
			return False
		elif self.agent.getHitpoints() == self.agent.getMaxHitpoints():
			# Exection succeeds
			print "exec", self.id, "true"
			return True
		else:
			# executing
			return None
		return ret

##################
### ChaseMinion
###
### Find the closest minion and move to intercept it.
### Parameters:
###   0: node ID string (optional)


class ChaseMinion(BTNode):

	### target: the minion to chase
	### timer: how often to replan

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		self.timer = 50
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.timer = 50
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		if len(enemies) > 0:
			best = None
			dist = 0
			for e in enemies:
				if isinstance(e, Minion):
					d = distance(self.agent.getLocation(), e.getLocation())
					if best == None or d < dist:
						best = e
						dist = d
			self.target = best
		if self.target is not None:
			navTarget = self.chooseNavigationTarget()
			if navTarget is not None:
				self.agent.navigateTo(navTarget)


	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None or self.target.isAlive() == False:
			# failed execution conditions
			print "exec", self.id, "false"
			return False
		elif self.target is not None and distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE:
			# succeeded
			print "exec", self.id, "true"
			return True
		else:
			# executing
			self.timer = self.timer - 1
			if self.timer <= 0:
				self.timer = 50
				navTarget = self.chooseNavigationTarget()
				if navTarget is not None:
					self.agent.navigateTo(navTarget)
			return None
		return ret

	def chooseNavigationTarget(self):
		if self.target is not None:
			return self.target.getLocation()
		else:
			return None

##################
### KillMinion
###
### Kill the closest minion. Assumes it is already in range.
### Parameters:
###   0: node ID string (optional)


class KillMinion(BTNode):

	### target: the minion to shoot

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.agent.stopMoving()
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		if len(enemies) > 0:
			best = None
			dist = 0
			for e in enemies:
				if isinstance(e, Minion):
					d = distance(self.agent.getLocation(), e.getLocation())
					if best == None or d < dist:
						best = e
						dist = d
			self.target = best


	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None or distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE:
			# failed executability conditions
			print "exec", self.id, "false"
			return False
		elif self.target.isAlive() == False:
			# succeeded
			print "exec", self.id, "true"
			return True
		else:
			# executing
			self.shootAtTarget()
			return None
		return ret

	def shootAtTarget(self):
		if self.agent is not None and self.target is not None:
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()


##################
### ChaseHero
###
### Move to intercept the enemy Hero.
### Parameters:
###   0: node ID string (optional)

class ChaseHero(BTNode):

	### target: the hero to chase
	### timer: how often to replan

	def ParseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		self.timer = 50
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.timer = 50
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		for e in enemies:
			if isinstance(e, Hero):
				self.target = e
				navTarget = self.chooseNavigationTarget()
				if navTarget is not None:
					self.agent.navigateTo(navTarget)
				return None


	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None or self.target.isAlive() == False:
			# fails executability conditions
			print "exec", self.id, "false"
			return False
		elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE:
			# succeeded
			print "exec", self.id, "true"
			return True
		else:
			# executing
			self.timer = self.timer - 1
			if self.timer <= 0:
				navTarget = self.chooseNavigationTarget()
				if navTarget is not None:
					self.agent.navigateTo(navTarget)
			return None
		return ret

	def chooseNavigationTarget(self):
		if self.target is not None:
			return self.target.getLocation()
		else:
			return None

##################
### KillHero
###
### Kill the enemy hero. Assumes it is already in range.
### Parameters:
###   0: node ID string (optional)


class KillHero(BTNode):

	### target: the minion to shoot

	def ParseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.agent.stopMoving()
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		for e in enemies:
			if isinstance(e, Hero):
				self.target = e
				return None

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None or distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE:
			# failed executability conditions
			if self.target == None:
				print "foo none"
			else:
				print "foo dist", distance(self.agent.getLocation(), self.target.getLocation())
			print "exec", self.id, "false"
			return False
		elif self.target.isAlive() == False:
			# succeeded
			print "exec", self.id, "true"
			return True
		else:
			#executing
			self.shootAtTarget()
			return None
		return ret

	def shootAtTarget(self):
		if self.agent is not None and self.target is not None:
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()


##################
### HitpointDaemon
###
### Only execute children if hitpoints are above a certain threshold.
### Parameters:
###   0: percentage of hitpoints that must be remaining to pass the daemon check
###   1: node ID string (optional)


class HitpointDaemon(BTNode):
	
	### percentage: percentage of hitpoints that must be remaining to pass the daemon check
	
	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.percentage = 0.5
		# First argument is the factor
		if len(args) > 0:
			self.percentage = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.agent.getHitpoints() < self.agent.getMaxHitpoints() * self.percentage:
			# Check failed
			print "exec", self.id, "fail"
			return False
		else:
			# Check didn't fail, return child's status
			return self.getChild(0).execute(delta)
		return ret

##################
### BuffDaemon
###
### Only execute children if agent's level is significantly above enemy hero's level.
### Parameters:
###   0: Number of levels above enemy level necessary to not fail the check
###   1: node ID string (optional)

class BuffDaemon(BTNode):

	### advantage: Number of levels above enemy level necessary to not fail the check

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.advantage = 0
		# First argument is the advantage
		if len(args) > 0:
			self.advantage = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		hero = None
		# Get a reference to the enemy hero
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		for e in enemies:
			if isinstance(e, Hero):
				hero = e
				break
		if hero == None or self.agent.level <= hero.level + self.advantage:
			# fail check
			print "exec", self.id, "fail"
			return False
		else:
			# Check didn't fail, return child's status
			return self.getChild(0).execute(delta)
		return ret





#################################
### MY CUSTOM BEHAVIOR CLASSES

class ParentRoot(BTNode):
    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        # First argument is the node ID
        if len(args) > 0:
            self.id = args[0]


    def execute(self, delta):
        BTNode.execute(self, delta)

        ret = self.getChild(0).execute()

        if len(self.agent.world.getEnemyNPCs(self.agent.team))>0 and self.agent.canFire() is True:
            enemies = self.agent.world.getEnemyNPCs(self.agent.team)

            closestEnemy = ''
            minDist = 0
            minPos = self.agent.getLocation()
            enemyIsClose = False

            for enemy in enemies:
                dist1 = distance(minPos, enemy.getLocation())
                if minDist == 0:
                    minDist = dist1
                    closestEnemy = enemy
                    if minDist<=250:
                        enemyIsClose = True
                elif dist1 < minDist:
                    minDist = dist1
                    closestEnemy = enemy
                    if minDist<=250:
                        enemyIsClose = True
            if enemyIsClose is True:
                self.agent.turnToFace(closestEnemy.getLocation())
                self.agent.shoot()

        if len(self.agent.world.getEnemyNPCs(self.agent.team))>0 and self.agent.areaEffectTimer is 0:
            self.agent.areaEffect()

        if len(self.agent.getVisibleType(Bullet))>0 and self.agent.dodgeTimer is 0:
            bullets = self.agent.getVisibleType(Bullet)

            closestBullet = ''
            minDist = 0
            minPos = self.agent.getLocation()
            bulletIsClose = False

            for bullet in bullets:
                dist1 = distance(minPos, bullet.getLocation())
                if minDist == 0:
                    minDist = dist1
                    closestBullet = bullet
                    if minDist <= 250:
                        bulletIsClose = True
                elif dist1 < minDist:
                    minDist = dist1
                    closestBullet = bullet
                    if minDist <= 250:
                        bulletIsClose = True
            if bulletIsClose is True:
                direction = (closestBullet.getLocation()[0] - self.agent.getLocation()[0], closestBullet.getLocation()[1] - self.agent.getLocation()[1])
                angle = math.degrees(numpy.arctan2(direction[0], direction[1])) - 180
                self.agent.dodge(angle)

        return ret

class BuffAndHPDaemon(BTNode):

    ### advantage: Number of levels above enemy level necessary to not fail the check

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.advantage = 0
        # First argument is the advantage
        if len(args) > 0:
            self.advantage = args[0]
        # Second argument is the node ID
        if len(args) > 1:
            self.id = args[1]

    def execute(self, delta = 0):
        ret = BTNode.execute(self, delta)
        hero = None
        # Get a reference to the enemy hero
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        for e in enemies:
            if isinstance(e, Hero):
                hero = e
                break
        if hero == None or self.agent.level <= hero.level + self.advantage:
            # fail check
            print "exec", self.id, "fail"
            return False
        elif (self.agent.level <= hero.level + self.advantage) and ((hero.getHitpoints()*1.0)/hero.getMaxHitpoints())>0.7 and (self.agent.getHitpoints()*1.0/self.agent.getMaxHitpoints())<0.6:
            # fail check
            print "exec", self.id, "fail"
            return False
        elif (self.agent.level <= hero.level + self.advantage) and ((hero.getHitpoints()*1.0)/hero.getMaxHitpoints())>0.5 and (self.agent.getHitpoints()*1.0/self.agent.getMaxHitpoints())<0.4:
            # fail check
            print "exec", self.id, "fail"
            return False
        else:
            # Check didn't fail, return child's status
            return self.getChild(0).execute(delta)
        return ret

class CustomKillHero(BTNode):

    ### target: the minion to shoot

    def ParseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.target = None
        # First argument is the node ID
        if len(args) > 0:
            self.id = args[0]

    def enter(self):
        BTNode.enter(self)
        self.agent.stopMoving()
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        for e in enemies:
            if isinstance(e, Hero):
                self.target = e
                return None

    def execute(self, delta = 0):
        ret = BTNode.execute(self, delta)
        if self.target == None or distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE:
            # failed executability conditions
            if self.target == None:
                print "foo none"
            else:
                print "foo dist", distance(self.agent.getLocation(), self.target.getLocation())
            print "exec", self.id, "false"
            return False
        elif self.target.isAlive() == False:
            # succeeded
            print "exec", self.id, "true"
            return True
        else:
            #executing
            self.shootAtTarget()

            if self.agent.areaEffectTimer is 0:
                self.agent.areaEffect()

            if len(self.agent.getVisibleType(Bullet)) > 0 and self.agent.dodgeTimer is 0:
                bullets = self.agent.getVisibleType(Bullet)

                closestBullet = ''
                minDist = 0
                minPos = self.agent.getLocation()
                bulletIsClose = False

                for bullet in bullets:
                    dist1 = distance(minPos, bullet.getLocation())
                    if minDist == 0:
                        minDist = dist1
                        closestBullet = bullet
                        if minDist <= 250:
                            bulletIsClose = True
                    elif dist1 < minDist:
                        minDist = dist1
                        closestBullet = bullet
                        if minDist <= 250:
                            bulletIsClose = True
                if bulletIsClose is True:
                    direction = (closestBullet.getLocation()[0] - self.agent.getLocation()[0],
                                 closestBullet.getLocation()[1] - self.agent.getLocation()[1])
                    angle = math.degrees(numpy.arctan2(direction[0], direction[1])) - 180
                    self.agent.dodge(angle)
            return None
        return ret

    def shootAtTarget(self):
        if self.agent is not None and self.target is not None:
            self.agent.turnToFace(self.target.getLocation())
            self.agent.shoot()

class CustomKillMinion(BTNode):

    ### target: the minion to shoot

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.target = None
        # First argument is the node ID
        if len(args) > 0:
            self.id = args[0]

    def enter(self):
        BTNode.enter(self)
        self.agent.stopMoving()
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        if len(enemies) > 0:
            best = None
            dist = 0
            for e in enemies:
                if isinstance(e, Minion):
                    d = distance(self.agent.getLocation(), e.getLocation())
                    if best == None or d < dist:
                        best = e
                        dist = d
            self.target = best


    def execute(self, delta = 0):
        ret = BTNode.execute(self, delta)
        if self.target == None or distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE:
            # failed executability conditions
            print "exec", self.id, "false"
            return False
        elif self.target.isAlive() == False:
            # succeeded
            print "exec", self.id, "true"
            return True
        else:
            # executing
            self.shootAtTarget()
            if self.agent.areaEffectTimer is 0:
                self.agent.areaEffect()

            if len(self.agent.getVisibleType(Bullet)) > 0 and self.agent.dodgeTimer is 0:
                bullets = self.agent.getVisibleType(Bullet)

                closestBullet = ''
                minDist = 0
                minPos = self.agent.getLocation()
                bulletIsClose = False

                for bullet in bullets:
                    dist1 = distance(minPos, bullet.getLocation())
                    if minDist == 0:
                        minDist = dist1
                        closestBullet = bullet
                        if minDist <= 250:
                            bulletIsClose = True
                    elif dist1 < minDist:
                        minDist = dist1
                        closestBullet = bullet
                        if minDist <= 250:
                            bulletIsClose = True
                if bulletIsClose is True:
                    direction = (closestBullet.getLocation()[0] - self.agent.getLocation()[0],
                                 closestBullet.getLocation()[1] - self.agent.getLocation()[1])
                    angle = math.degrees(numpy.arctan2(direction[0], direction[1])) - 180
                    self.agent.dodge(angle)
            return None
        return ret

    def shootAtTarget(self):
        if self.agent is not None and self.target is not None:
            self.agent.turnToFace(self.target.getLocation())
            self.agent.shoot()

class NoMoreThanNEnemiesDaemon(BTNode):

    ### advantage: Number of levels above enemy level necessary to not fail the check

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.numEnemies = 3
        # First argument is the advantage
        if len(args) > 0:
            self.numEnemies = args[0]
        # Second argument is the node ID
        if len(args) > 1:
            self.id = args[1]

    def execute(self, delta = 0):
        ret = BTNode.execute(self, delta)
        hero = None
        # Get a reference to the enemy hero
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())

        numEnemies = 0
        minPos = self.agent.getLocation()

        for enemy in enemies:
            dist1 = distance(minPos, enemy.getLocation())
            if dist1<=250:
                numEnemies=numEnemies+1

        if numEnemies>=self.numEnemies:
            # fail check
            print "exec", self.id, "fail"
            return False
        else:
            # Check didn't fail, return child's status
            return self.getChild(0).execute(delta)
        return ret
