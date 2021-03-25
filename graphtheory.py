#!/usr/bin/env python3

import pygame
import math as maths
import sys

COLOUR_BG = (0, 0, 0)
COLOUR_FG = (255, 255, 255)
COLOUR_SELECTED = (0, 255, 0)
COLOUR_DELETE = (255, 0, 0)

def createNode(position = (0,0)):
	nodes.append(pygame.rect.Rect(position[0], position[1], node_size, node_size))

def createEdge(node1, node2):
	#if((node1 in nodes) and (node2 in nodes) and (not(isConnected(node1, node2)))):
	#	edges.append([node1, node2])
	#else:
	#	raise(TypeError("Edge already exists or nodes do not exist"))
	edges.append([node1, node2])

def arrangeNodes(radius, offset):
	n = len(nodes)
	factor = 2 * maths.pi / n
	for i in range(n):
		x_i = radius * maths.cos(factor * i) + offset[0]
		y_i = radius * maths.sin(factor * i) + offset[1]
		nodes[i].x = int(x_i)
		nodes[i].y = int(y_i)

def focusNode(node, radius, offset):
	node.x = offset[0]
	node.y = offset[1]
	n = len(nodes)
	factor = 2 * maths.pi / (n - 1)
	for i in range(n):
		if(node != nodes[i]):
			x_i = radius * maths.cos(factor * i) + offset[0]
			y_i = radius * maths.sin(factor * i) + offset[1]
			nodes[i].x = x_i
			nodes[i].y = y_i

def isConnected(node1, node2):
	return(([node1, node2] in edges) or ([node2, node1] in edges))

if(__name__ == "__main__"):
	pygame.init()
	size = (1600, 900)
	surface = pygame.display.set_mode(size, pygame.RESIZABLE)
	pygame.display.set_caption("Graph Theory")
	font = pygame.font.SysFont("monospace", 60)
	clock = pygame.time.Clock()

	screenCentre = (int(size[0] / 2), int(size[1] / 2))

	run = True
	drag = False #drag node
	scroll = False #drag screen (i.e. scrolling)
	selected = None
	node_size = 8
	line_width = 2

	edges = []
	nodes = []
	#createNode((500, 500))
	#createNode((700, 200))
	#createEdge(nodes[0], nodes[1])
	for i in range(4):
		createNode()
	for i in range(4):
		for j in range(i, 4): #range(i, 4) to not create duplicate edges
			if(i != j):
				createEdge(nodes[i], nodes[j])
	arrangeNodes(100, screenCentre)
	while(run):
		for event in pygame.event.get():
			if(event.type == pygame.QUIT):
				run = False
			elif(event.type == pygame.VIDEORESIZE):
				factor = (event.w / size[0], event.h / size[1]) #rescale factor
				size = (event.w, event.h)
				screencentre = (int(event.w / 2), int(event.h / 2))
				surface = pygame.display.set_mode(size, pygame.RESIZABLE)
				for node in nodes:
					node.x = int(node.x * factor[0])
					node.y = int(node.y * factor[1])
			elif(event.type == pygame.KEYDOWN):
				if(str(event.unicode) == "q"):
					run = False
				elif(str(event.unicode) == "a"):
					arrangeNodes(100, screenCentre)
				elif(str(event.unicode) == "f"):
					if(selected is not None):
						focusNode(selected, 100, screenCentre)
						selected = None
				elif(str(event.unicode) == "n"):
					createNode(screenCentre)
				elif(str(event.unicode) == "-"):
					node_size -= 1
					for node in nodes:
						node.w = node_size
						node.h = node_size
				elif(str(event.unicode) == "="):
					node_size += 1
					for node in nodes:
						node.w = node_size
						node.h = node_size
				elif(str(event.unicode) == "_"):
					line_width -= 1
				elif(str(event.unicode) == "+"):
					line_width += 1
			elif(event.type == pygame.MOUSEBUTTONDOWN):
				if(event.button == 1): #left click - moves nodes
					for node in nodes:
						if(node.collidepoint(event.pos)):
							drag = True
							node1 = node
							mouse_x, mouse_y = event.pos
							dx = node1.x - mouse_x
							dy = node1.y - mouse_y
							break
					if(not(drag)):
						scroll = True
						mouse_x, mouse_y = event.pos
						dxs = [node.x - mouse_x for node in nodes]
						dys = [node.y - mouse_y for node in nodes]
				elif(event.button == 2): #middle click - deletes nodes
					edges_new = []
					for node in nodes:
						if(node.collidepoint(event.pos)):
							for edge in edges:
								if(node not in edge):
									edges_new.append(edge)
							nodes.remove(node)
							edges = edges_new
				elif(event.button == 3): #right click - connects/disconnects nodes
					for node in nodes:
						if(node.collidepoint(event.pos)):
							if((selected is not None) and (node != selected)):
								if([selected, node] in edges): #no duplicate edges
									edges.remove([selected, node])
								elif([node, selected] in edges):
									edges.remove([node, selected])
								else:
									edges.append([selected, node])
								selected = None
							elif((selected is not None) and (node == selected)):
								selected = None
							else:
								selected = node
			elif(event.type == pygame.MOUSEBUTTONUP):
				if(event.button == 1):
					drag = False
					scroll = False
			elif(event.type == pygame.MOUSEMOTION):
				if(drag):
					mouse_x, mouse_y = event.pos
					node1.x = mouse_x + dx
					node1.y = mouse_y + dy
				if(scroll):
					mouse_x, mouse_y = event.pos
					for i in range(len(nodes)):
						nodes[i].x = mouse_x + dxs[i]
						nodes[i].y = mouse_y + dys[i]
			elif(event.type == pygame.MOUSEWHEEL):
				mouse_x, mouse_y = pygame.mouse.get_pos()
				scroll_amount = event.y
				for node in nodes:
					dx, dy = (node.x - mouse_x, node.y - mouse_y)
					dx *= 1.1 ** scroll_amount
					dy *= 1.1 ** scroll_amount
					node.x = mouse_x + dx
					node.y = mouse_y + dy
		surface.fill(COLOUR_BG)
		for edge in edges:
			colour = COLOUR_SELECTED if(selected in edge) else COLOUR_FG
			pygame.draw.line(surface, colour, edge[0].center, edge[1].center, line_width)
		for node in nodes: #looks nicer with nodes on top of edges
			colour = COLOUR_SELECTED if(node == selected) else COLOUR_FG
			pygame.draw.rect(surface, colour, node)
		pygame.display.flip()
		clock.tick(60)
	pygame.quit()
	sys.exit()
