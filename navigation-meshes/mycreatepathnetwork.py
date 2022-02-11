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


import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

from random import shuffle


def myCreatePathNetwork(world, agent=None):
	nodes = []
	edges = []
	polys = []
	### YOUR CODE GOES BELOW HERE ###

	#gets the points of all the obstacles in the game world
	points = world.getPoints()
	#gets all the lines of obstacles in the game world
	worldLines = world.getLines()
	#gets the obstacle objects in the game world
	worldObstacles = world.getObstacles()
	#randomizes the points of the obstacles in the game world
	random.shuffle(points)
	#getting the radius of the agent in the game world
	radius = agent.getMaxRadius()

	#looping through and getting three points
	#looping in a way that I will not have duplicates
	for x in range(len(points)):
		for y in range(x+1,len(points)):
			for z in range (y+1, len(points)):
				#boolean that keeps track if the polygon crosses an obstacle
				lineCheck = True
				#getting the midpoints of the edges of the polygon
				midpoint1 = ((points[x][0] + points[y][0]) / 2, (points[x][1] + points[y][1]) / 2)
				midpoint2 = ((points[x][0] + points[z][0]) / 2, (points[x][1] + points[z][1]) / 2)
				midpoint3 = ((points[y][0] + points[z][0]) / 2, (points[y][1] + points[z][1]) / 2)
				#the polygon that is made from the three chosen points
				polylines = ((points[x], points[y]), (points[x], points[z]), (points[y], points[z]))

				# checking that no rules have been broken
				if (lineCheck):
					# getting the number of obstacles in the game world
					obstaclesLength = len(worldObstacles)
					# looping through each obstacle
					for k in range(obstaclesLength):
						# getting a single obstacle
						obstacle = worldObstacles[k]
						#getting the midpoint of the obstacle object
						midpointX = 0
						midpointY = 0
						# getting all the points of the obstacle object to determine the center
						obstaclePoints = obstacle.getPoints()
						obstPointLength = len(obstaclePoints)
						# calculating the midpoint of the obstacle
						for l in range(obstPointLength):
							midpointX = midpointX + obstaclePoints[l][0]
							midpointY = midpointY + obstaclePoints[l][1]
						midpointX = midpointX/obstPointLength
						midpointY = midpointY/obstPointLength
						#if the center of the obstacle is in the polygon, the polygon is not valid
						# the check causes it to break out of the current iteration and goes to the next valid polygon
						if pointInsidePolygonLines((midpointX, midpointY), polylines):
							lineCheck = False
							break

				# checks if the previous case passed
				if(lineCheck):
					# checks if the lines of the polygon are intersecting any of the lines of the obstacles
					linesLength = len(worldLines)
					for i in range(linesLength):
						line = worldLines[i]
						if ((rayTraceNoEndpoints(points[x], points[y], line) != None and (points[x], points[y]) not in worldLines and (points[y], points[x]) not in worldLines)
							or (rayTraceNoEndpoints(points[x], points[z], line) != None and (points[x], points[z]) not in worldLines and (points[z], points[x]) not in worldLines)
							or (rayTraceNoEndpoints(points[y], points[z], line) != None and (points[y], points[z]) not in worldLines and (points[z], points[y]) not in worldLines)):
								lineCheck = False
								break

				# checks if the previous two cases passed
				if(lineCheck):
					# checks if the midpoints of the edges of the polygon are inside any of the objects
					obstaclesLength = len(worldObstacles)
					for j in range(obstaclesLength):
						obstacle = worldObstacles[j]
						obstLines = obstacle.getLines()
						if (pointInsidePolygonLines(midpoint1,obstLines) and (points[x], points[y]) not in worldLines and (points[y], points[x]) not in worldLines
						or pointInsidePolygonLines(midpoint2,obstLines) and (points[x], points[z]) not in worldLines and (points[z], points[x]) not in worldLines
						or pointInsidePolygonLines(midpoint3,obstLines) and (points[y], points[z]) not in worldLines and (points[z], points[y]) not in worldLines):
							lineCheck = False
							break

				# if all the cases passed, the polygon gets added to the list of polygons
				# the polygon also gets added as a new obstacle, so new polygons don't intersect with it
				if (lineCheck):
					polys.append((points[x], points[y], points[z]))
					worldLines.extend(polylines)


	# takes all the polygons and combines the ones that are sharing an edge
	origLength = len(polys)
	# the maximum number of times it is going to iterate through two sets of polygons
	# needs to loop from this point because the number of polygons are going to change based on combining two of them
	for p in range(origLength):
		# keeps track of triangles that have been combined to remove
		toRemove = []
		polyLength = len(polys)
		# boolean value that will cause the for loop to break because two polygons are combined when the product is adjacent and convex
		isconvex = False
		#looping through two polygons
		for m in range(polyLength):
			for n in range(m + 1, polyLength):
				poly1 = polys[m]
				poly2 = polys[n]
				#checks if two polygons are adjacent
				isAdjacent = polygonsAdjacent(poly1, poly2)
				# if they are adjacent, we get a combined set of points to prepare for combining
				if isAdjacent:
					polyPoints = list(poly1)
					for point in poly2:
						if not(point in polyPoints):
							polyPoints.append(point)

					# code based on https://math.stackexchange.com/questions/978642/how-to-sort-vertices-of-a-polygon-in-counter-clockwise-order
					# we are ordering them based on the java code and algorithm from the link above
					####################################################################################################
					midX = 0
					midY = 0
					for d in range(len(polyPoints)):
						midX = midX + polyPoints[d][0]
						midY = midY + polyPoints[d][1]
					midX = midX / len(polyPoints)
					midY = midY / len(polyPoints)

					dict = {}
					list_ = []

					for d in range(len(polyPoints)):
						angle = (math.degrees(math.atan2(polyPoints[d][1] - midY, polyPoints[d][0] - midX)) + 360) % 360
						list_.append(angle)
						dict[angle] = (polyPoints[d][0], polyPoints[d][1])

					list_.sort()
					newPoints = []
					for item in list_:
						newPoints.append(dict[item])
					####################################################################################################
					# checking if the product of the two polygons is convex
					isconvex = isConvex(newPoints) and isAdjacent
					#if product is convex, we add it to polys and set its predecessors for removal
					if isconvex and isAdjacent:
						polys.append(newPoints)
						toRemove.append(poly1)
						toRemove.append(poly2)
						#break to adjust for the change in polygon numbers
						break
			# if the product is convex, we are removing the two polygons and breaking again
			if isconvex:
				for poly in toRemove:
					if poly in polys:
						polys.remove(poly)
				break

	polynodes = []
	# adding the nodes of the polygons to the global set
	polyLength = len(polys)
	for c in range(polyLength):
		poly = polys[c]
		polyLength = len(poly)
		midX = 0
		midY = 0
		for d in range(polyLength):
			midX = midX + poly[d][0]
			midY = midY + poly[d][1]
		midX = midX / polyLength
		midY = midY / polyLength
		nodes.append((midX, midY))
		polynodes.append((poly, (midX, midY)))

	# adding the edges of the polygons to the global set
	for e in range(len(polys)):
		for f in range(e, len(polys)):
			poly1 = polys[e]
			poly2 = polys[f]
			isAdjacent = polygonsAdjacent(poly1, poly2)
			sharedSide = []
			if isAdjacent:
				for x in poly1:
					if x in poly2:
						sharedSide.append(x)
				if distance(sharedSide[0], sharedSide[1]) > (radius*1.25):
					nodes.append(tuple(numpy.array((sharedSide[0]))+numpy.array((sharedSide[1]))/2))
					centers = []
					for (poly,center) in polynodes:
						if poly in [poly1, poly2]:
							centers.append(center)
					for center in centers:
						edges.append(((tuple(numpy.array((sharedSide[0]))+numpy.array((sharedSide[1]))/2)), center))
	### YOUR CODE GOES ABOVE HERE ###
	return nodes, edges, polys