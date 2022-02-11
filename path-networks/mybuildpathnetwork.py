'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Jeyanth John Britto 01/2019
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

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates the path network as a list of lines between all path nodes that are traversable by the agent.
def myBuildPathNetwork(pathnodes, world, agent = None):

	lines = []
	### YOUR CODE GOES BELOW HERE ###
	# get the length of path nodes for for loops
	numPathNodes = len(pathnodes)
	# make a copy of path nodes
	pathnodes_cp = list(pathnodes)
	# get all the obstacles in the game world
	obstacles = world.getObstacles()
	# get the lines of obstacles in the game world
	worldLines = world.getLines()

	# removing points that are obstacles
	# looping through each obstacle
	for obstacle in obstacles:
		# looping through each path node
		for x in range(numPathNodes):
			# if path node is in the obstacle, remove it from the path nodes list
			if obstacle.pointInside(pathnodes[x]) is True:
				# removing from path nodes list
				pathnodes_cp.remove(pathnodes[x])

	# getting the length of the update path nodes copy
	numPathNodes_cp = len(pathnodes_cp)

	# looping through 2 path nodes
	for i in range(numPathNodes_cp):
		# getting the first path node
		pathNode1 = pathnodes_cp[i]
		# starting from where the previous loop starts, so there won't be duplicate lines
		for j in range(i,numPathNodes_cp):
			# no need to compare the same path nodes
			if(i is not j):
				# getting the second path node
				pathNode2 = pathnodes_cp[j]

				# boolean value that will tell me if the line is intersected by an object or edges
				lineCheck = True

				# loops through each line of the obstacles and tells me if the the lines intersect
				for line in worldLines:
					# checks if the lines intersect
					if rayTrace(pathNode1,pathNode2,line) is not None:
						# if lines intersect change the value to false and break out the loop
						lineCheck = False
						break

				# if line does intersect, no need to add it to our path network
				if(lineCheck):
					lines.append(tuple((pathNode1,pathNode2)))

	# making a list of lines to remove
	linesToRemove = []
	# looping through the objects
	for obstacle in obstacles:
		# gets the points of the obstacles
		obstaclepoints = obstacle.getPoints()
		# get the length of the points of obstacles
		lenobstpoints = len(obstaclepoints)

		# looping through the points
		for k in range(lenobstpoints):

			# getting the list of lines
			lenlines = len(lines)
			# looping through the list of lines
			for l in range(lenlines):
				# checking if the agent will be able to traverse the path based on size or radius
				# multiplying the radius by slightly more than 1 to make sure it will comfortably fit
				if (agent.getRadius()*1.125) > minimumDistance(lines[l], obstaclepoints[k]):
					# making sure there are no duplicates in the lines to remove
					if not (lines[l] in linesToRemove):
						# if the agent is too big to traverse the path, the line will be removed
						linesToRemove.append(lines[l])

	# for each line in line to remove, remove it from our lines list
	for line in linesToRemove:
		lines.remove(line)

	### YOUR CODE GOES ABOVE HERE ###
	return lines

