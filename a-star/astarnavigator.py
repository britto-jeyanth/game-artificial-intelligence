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
from mycreatepathnetwork import *
from mynavigatorhelpers import *


###############################
### AStarNavigator
###
### Creates a path node network and implements the A* algorithm to create a path to the given destination.
			
class AStarNavigator(NavMeshNavigator):

	def __init__(self):
		NavMeshNavigator.__init__(self)
		

	### Create the path node network.
	### self: the navigator object
	### world: the world object
	def createPathNetwork(self, world):
		self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
		return None
		
	### Finds the shortest path from the source to the destination using A*.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., its current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		self.setPath(None)
		### Make sure the next and dist matrices exist
		if self.agent != None and self.world != None: 
			self.source = source
			self.destination = dest
			### Step 1: If the agent has a clear path from the source to dest, then go straight there.
			###   Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
			###   Tell the agent to move to dest
			### Step 2: If there is an obstacle, create the path that will move around the obstacles.
			###   Find the path nodes closest to source and destination.
			###   Create the path by traversing the self.next matrix until the path node closest to the destination is reached
			###   Store the path by calling self.setPath()
			###   Tell the agent to move to the first node in the path (and pop the first node off the path)
			if clearShot(source, dest, self.world.getLinesWithoutBorders(), self.world.getPoints(), self.agent):
				self.agent.moveToTarget(dest)
			else:
				start = findClosestUnobstructed(source, self.pathnodes, self.world.getLinesWithoutBorders())
				end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLinesWithoutBorders())
				if start != None and end != None:
					# print len(self.pathnetwork)
					newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates())
					# print len(newnetwork)
					closedlist = []
					path, closedlist = astar(start, end, newnetwork)
					if path is not None and len(path) > 0:
						path = shortcutPath(source, dest, path, self.world, self.agent)
						self.setPath(path)
						if self.path is not None and len(self.path) > 0:
							first = self.path.pop(0)
							self.agent.moveToTarget(first)
		return None
		
	### Called when the agent gets to a node in the path.
	### self: the navigator object
	def checkpoint(self):
		myCheckpoint(self)
		return None

	### This function gets called by the agent to figure out if some shortcuts can be taken when traversing the path.
	### This function should update the path and return True if the path was updated.
	def smooth(self):
		return mySmooth(self)

	def update(self, delta):
		myUpdate(self, delta)


def unobstructedNetwork(network, worldLines):
	newnetwork = []
	for l in network:
		hit = rayTraceWorld(l[0], l[1], worldLines)
		if hit == None:
			newnetwork.append(l)
	return newnetwork




def astar(init, goal, network):
	path = []
	open = []
	closed = []
	### YOUR CODE GOES BELOW HERE ###
	pairs = []
	open.append(init)
	open_dict = {}
	close_dict = {}
	open_dict[init]={}
	open_dict[init]['g']=0
	open_dict[init]['h']=0
	open_dict[init]['f']=0
	found = False
	# print 'start'
	while(len(open)>0):
		q = open[0]
		f = open_dict[q]['f']
		# print 'open list'
		# print open
		# print open_dict
		for i in open:
			if open_dict[i]['f'] < f:
				f = open_dict[i]['f']
				q = i
		#open.remove(q)
		succesor = []
		succesor_dict = {}
		# print q

		if found == True:
			close_dict[q] = {}
			close_dict[q]['g'] = open_dict[q]['g']
			close_dict[q]['h'] = open_dict[q]['g']
			open_dict.pop(q)
			closed.append(q)
			pairs.append((closed[len(closed) - 1], q))
			break



		dist = 0
		x = 0
		y = 0
		if found == True:
			break

		#print network
		open = []
		for a,b in network:
			if a[0]==q[0] and a[1]==q[1] and b not in succesor:
				succesor.append(b)
				if b is goal:
					found=True
					break
			if b[0]==q[0] and b[1]==q[1] and a not in succesor:
				succesor.append(a)
				if a is goal:
					found=True
					break
		# print succesor

		for s in succesor:
			succesor_dict[s] = {}
			# print 'here1'
			# print open_dict
			# print q
			# print 'here2'
			succesor_dict[s]['g'] = open_dict[q]['g'] + distance(q,s)
			succesor_dict[s]['h'] = open_dict[q]['h'] + distance(goal, s)
			succesor_dict[s]['f'] = succesor_dict[s]['h']+succesor_dict[s]['g']
			if s in close_dict:
				succesor_f = succesor_dict[s]['f']
				old_f = close_dict[s]['h']
				if succesor_f<old_f:
					open_dict[s]['g'] = succesor_dict[s]['g']
					open_dict[s]['h'] = succesor_dict[s]['h']
					open_dict[s]['f'] = succesor_dict[s]['f']
			else:
				open.append(s)
				open_dict[s] = {}
				open_dict[s]['g'] = succesor_dict[s]['g']
				open_dict[s]['h'] = succesor_dict[s]['h']
				open_dict[s]['f'] = succesor_dict[s]['f']
		close_dict[q] = {}
		close_dict[q]['g'] = open_dict[q]['g']
		close_dict[q]['h'] = open_dict[q]['h']
		open_dict.pop(q)
		if len(closed)>0:
			pairs.append((closed[len(closed)-1],q))
		closed.append(q)
	# 	print
	# 	# print(succesor_dict)
	# print closed
	# print pairs
	# path.append(init)
	# for c in closed:
	# 	if c not in path:
	path = closed
	### YOUR CODE GOES ABOVE HERE ###
	return path, closed


def myUpdate(nav, delta):
	### YOUR CODE GOES BELOW HERE ###
	bool1 = nav.getDestination() is None
	agent = nav.agent
	bool2 = clearShot(agent.getLocation(), agent.getMoveTarget(), nav.world.getLines(),nav.world.getPoints, agent) is True
	if(bool1):
		return None
	else:
		agent = nav.agent
		if bool2:
			return None
		else:
			agent.navigateTo(dest)
	if(not bool1 and not bool2 and nav.getPath() is None):
		agent.stop()
	### YOUR CODE GOES ABOVE HERE ###
	return None



def myCheckpoint(nav):
	### YOUR CODE GOES BELOW HERE ###
	new_path = False
	agent = nav.agent
	path = []
	path.append(agent.getLocation())
	path.append(agent.getMoveTarget())
	path.extend(nav.getPath())
	path.append(nav.getDestination())

	for point in path:
		bool_1 = path.index(point) == (len(path)-1)
		if bool_1:
			break
		else:
			bool_2 = clearShot(point, path[path.index(point)+1], nav.world.getLines(), nav.world.getPoints, agent)
			if not bool_2:
				new_path=True
				break
	if new_path:
		agent.stop()
		agent.navigateTo(nav.getDestination())
		agent.start()

	### YOUR CODE GOES ABOVE HERE ###
	return None


### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
	### YOUR CODE GOES BELOW HERE ###

	radius = agent.getMaxRadius()
	dist = distance(p1,p2)
	x_diff = p2[0] - p1[0]
	y_diff = p2[1] - p1[1]
	lineCheck=True

	if dist <=0:
		return lineCheck
	y = -x_diff*radius/dist
	x = y_diff*radius/dist
	p1 = p1+ (x,y)
	p2 = p2 + (x,y)
	for line in worldLines:
		if rayTrace(p1, p2, line) is not None:
			lineCheck = False
			break
	if lineCheck==True:
		x=-x*2
		y=-y*2

		p1 = p1 + (x, y)
		p2 = p2 + (x, y)
		for line in worldLines:
			if rayTrace(p1, p2, line) is not None:
				lineCheck = False
				break
		if lineCheck==True:
			x = -x / 2
			y = -y / 2
			p1 = p1 + (x, y)
			p2 = p2 + (x, y)

			for line in worldLines:
				if (radius * 1.125) > minimumDistance(line, p1):
					lineCheck = False
					break
			if lineCheck==True:
				for line in worldLines:
					if (radius * 1.125) > minimumDistance(line, p2):
						lineCheck = False
						break
				return lineCheck
			else:
				return False
		else:
			return False
	else:
		return False
	### YOUR CODE GOES ABOVE HERE ###
	return False

