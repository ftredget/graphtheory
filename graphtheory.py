#!/usr/bin/env python3

import pygame
import math as maths
import sys
import os
import json
import datetime

COLOUR_BG       = (  0,   0,   0)
COLOUR_FG       = (255, 255, 255)
COLOUR_SELECTED = (  0, 255,   0)
COLOUR_DELETE   = (255,   0,   0)

def now():
    return(datetime.datetime.now().isoformat().split(".")[0])

def export_json(filename = ""):
    if(filename == ""):
        filename = "graph_" + now() + ".json"
    nodes_json = [{"name": node[2], "position": node[1].center} for node in nodes]
    full_json  = {"nodes": nodes_json, "edges": edges}
    path = os.path.dirname(os.path.realpath(__file__))
    file = open(path + "/" + filename, "w")
    file.write(json.dumps(full_json, indent=4))
    file.close()

def import_json(filename):
    path = os.path.dirname(os.path.realpath(__file__))
    file = open(path + "/" + filename, "r")
    file_contents = json.loads(file.read())
    file.close()
    nodes_json = file_contents["nodes"]
    nodes0 = []
    for node in nodes_json:
        text           = font.render(node["name"], True, COLOUR_FG, COLOUR_BG)
        textbox        = text.get_rect()
        textbox.center = node["position"]
        nodes0.append([text, textbox, node["name"]])
    edges0 = file_contents["edges"]
    return([nodes0, edges0])

def toggle_import():
    global file_menu
    global menu
    file_menu = not(file_menu)
    if(file_menu):
        path  = os.path.dirname(os.path.realpath(__file__))
        jsons = [file for file in os.listdir(path) if file[-5:] == ".json"]
        menu  = []
        for (i, json) in enumerate(jsons):
            text       = font.render(json, True, COLOUR_FG, COLOUR_BG)
            box        = text.get_rect()
            box.center = [size[0] / 2, size[1] / 2 - 1.5 * (len(jsons)/2-i) * font_size]
            menu.append([text, box, json])

def createNode(position = (0,0), label = ""):
    global edges
    global nodes
    text = font.render(label, True, COLOUR_FG, COLOUR_BG)
    textbox = text.get_rect()
    textbox.center = position
    nodes.append([text, textbox, label])
    for row in edges:
        row.append(0)
    edges.append([0 for node in nodes])
    edges[-1][-1] = 1

def deleteNode(node):
    nodes.remove(nodes[node])
    for row in edges:
        row[node] = None #Setting the value to None means it will delete the correct item
        row.remove(None) #instead of the first item with the same value
    edges[node] = None
    edges.remove(None)

def createEdge(node1, node2):
    edges[node1][node2] += 1
    edges[node2][node1] += 1

def arrangeNodes(radius, offset):
    n = len(nodes)
    factor = 2 * maths.pi / n
    for i in range(n):
        x_i = radius * maths.cos(factor * i) + offset[0]
        y_i = radius * maths.sin(factor * i) + offset[1]
        nodes[i][1].center = (int(x_i), int(y_i))

def focusNode(node, radius, offset):
    node[1].center = offset
    n      = len(nodes)
    factor = 2 * maths.pi / (n - 1)
    past   = 0 #If we have iterated past node
    for i in range(n):
        if(nodes[i] != node):
            x_i = radius * maths.cos(factor * (i - past)) + offset[0]
            y_i = radius * maths.sin(factor * (i - past)) + offset[1]
            nodes[i][1].center = (int(x_i), int(y_i))
        else:
            past = 1

def changeZoom(centre, amount):
    global nodes
    for node in nodes:
        dx, dy = (node[1].x - centre[0], node[1].y - centre[1])
        dx *= 1.1 ** amount
        dy *= 1.1 ** amount
        node[1].x = centre[0] + dx
        node[1].y = centre[1] + dy

def isConnected(node1, node2):
    return(bool(edges[node1, node2]))

def quitProgram():
    global run
    run = False

def focus():
    global selected
    if(selected):
        focusNode(selected, 200, screenCentre)
        selected[0] = font.render(selected[2], True, COLOUR_FG, COLOUR_BG)
        selected = None

def clear():
    global edges
    edges = [[int(node_a==node_b) for node_a in nodes] for node_b in nodes]

def complete():
    global edges
    edges = [[1 for node_a in nodes] for node_b in nodes]

def changeFontSize(changeInFontSize):
    global font_size
    global font
    font_size = font_size + changeInFontSize
    font = pygame.font.SysFont("monospace", font_size)
    for node in nodes:
        node[0] = font.render(node[2], True, COLOUR_FG, COLOUR_BG)
        centre  = node[1].center
        node[1] = node[0].get_rect()
        node[1].center = centre

def changeLineWidth(changeInLineWidth):
    global line_width
    line_width = line_width + changeInLineWidth

def printStatus():
    print(edges)
    print([node[2] for node in nodes])

def rename():
    global renaming
    renaming = True if selected is not None else False

def debug():
    print("selected: ", selected)
    print("renaming: ", renaming)
    print("drag: ", drag)
    print("scroll: ", scroll)
    print("file_menu: ", file_menu)

keys = {"q": [quitProgram, "quit"],
        "a": [lambda: arrangeNodes(200, screenCentre), "arrange nodes"],
        "f": [focus, "focus node"],
        "n": [lambda: createNode(screenCentre, label = str(len(nodes))), "new node"],
        "c": [clear, "clear all edges"],
        "k": [complete, "connect all nodes"],
        "=": [lambda: changeFontSize(5), "increase font size"],
        "-": [lambda: changeFontSize(-5), "decrease font size"],
        "+": [lambda: changeLineWidth(1), "increase line width"],
        "_": [lambda: changeLineWidth(-1), "decrease line width"],
        "]": [lambda: changeZoom(screenCentre, 1), "zoom in"],
        "[": [lambda: changeZoom(screenCentre, -1), "zoom out"],
        "p": [printStatus, "print status"],
        "e": [export_json, "export json"],
        "i": [toggle_import, "import json"],
        "r": [rename, "rename node"],
        "d": [debug, "debug"]
}

if(__name__ == "__main__"):
    pygame.init()
    size = (1600, 900)
    surface = pygame.display.set_mode(size, pygame.RESIZABLE)
    pygame.display.set_caption("Graph Theory")
    clock = pygame.time.Clock()

    screenCentre = (size[0] / 2, size[1] / 2)

    run = True
    drag = False #drag node
    scroll = False #drag screen (i.e. scrolling)
    renaming = False
    selected = None
    file_menu = False
    line_width = 2
    font_size = 40
    font = pygame.font.SysFont("monospace", font_size)

    nodes = []
    edges = []
    toggle_import()

    while(run):
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                run = False
            elif(event.type == pygame.VIDEORESIZE):
                factor = (event.w / size[0], event.h / size[1]) #rescale factor
                size = (event.w, event.h)
                screenCentre = (event.w / 2, event.h / 2)
                surface = pygame.display.set_mode(size, pygame.RESIZABLE)
                for node in nodes:
                    node[1].x = int(node[1].x * factor[0])
                    node[1].y = int(node[1].y * factor[1])
            elif((event.type == pygame.KEYDOWN) and not(renaming)):
                if(str(event.unicode) in keys):
                    keys[str(event.unicode)][0]()
                else:
                    if((file_menu) and (event.key == pygame.K_ESCAPE)):
                        file_menu = False
            elif((event.type == pygame.KEYDOWN) and (renaming) and not(file_menu)):
                if(event.key == pygame.K_BACKSPACE):
                    selected[2] = selected[2][:-1]
                elif((event.key == pygame.K_RETURN) or (event.key == pygame.K_ESCAPE)):
                    selected[0] = font.render(selected[2], True, COLOUR_FG, COLOUR_BG)
                    renaming = False
                    selected = None
                    break
                else:
                    selected[2] += str(event.unicode)
                centre = selected[1].center
                selected[0] = font.render(selected[2], True, COLOUR_SELECTED, COLOUR_BG)
                selected[1] = selected[0].get_rect()
                selected[1].center = centre
            elif((event.type == pygame.MOUSEBUTTONDOWN) and not(file_menu)):
                if(event.button == 1): #left click - moves nodes
                    for node in nodes:
                        if(node[1].collidepoint(event.pos)):
                            drag = True
                            node1 = node
                            mouse_x, mouse_y = event.pos
                            dx = node1[1].x - mouse_x
                            dy = node1[1].y - mouse_y
                            break
                    if(not(drag)):
                        scroll = True
                        mouse_x, mouse_y = event.pos
                        dxs = [node[1].x - mouse_x for node in nodes]
                        dys = [node[1].y - mouse_y for node in nodes]
                elif(event.button == 2): #middle click - deletes nodes
                    for node in nodes:
                        if(node[1].collidepoint(event.pos)):
                            deleteNode(nodes.index(node))
                elif(event.button == 3): #right click - connects/disconnects nodes
                    v = 1
                    for node in nodes:
                        if(node[1].collidepoint(event.pos)):
                            v *= 0
                            if((selected is not None) and (node != selected)):
                                node_i = nodes.index(node)
                                selected_i = nodes.index(selected)
                                if(edges[selected_i][node_i] and not(pygame.key.get_mods() & pygame.KMOD_SHIFT)): #not holding shift connects disconnected pairs, disconnects connected pairs
                                    edges[selected_i][node_i] = max(0, edges[selected_i][node_i]-1)
                                    edges[node_i][selected_i] = edges[selected_i][node_i]
                                else: #holding shift allows multiple connections between nodes
                                    edges[selected_i][node_i] += 1
                                    edges[node_i][selected_i] += 1
                                if(not(renaming)): #if not renaming, deselect nodes
                                    selected[0] = font.render(selected[2], True, COLOUR_FG, COLOUR_BG)
                                    selected = None
                                    node[0] = font.render(node[2], True, COLOUR_FG, COLOUR_BG)
                            elif((selected is not None) and (node == selected)): #Right clicking on the selected node deselects it
                                selected = None
                                renaming = False
                                node[0] = font.render(node[2], True, COLOUR_FG, COLOUR_BG)
                            else:
                                selected = node
                                node[0] = font.render(node[2], True, COLOUR_SELECTED, COLOUR_BG)
                    if(v and (selected is not None)):
                        selected[0] = font.render(selected[2], True, COLOUR_FG, COLOUR_BG)
                        selected = None
                        renaming = False
            elif((event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1) and (file_menu)):
                v = 1
                for item in menu:
                    if(item[1].collidepoint(event.pos)):
                        v *= 0
                        nodes, edges = import_json(item[2])
                        file_menu = False
                if(v):
                    file_menu = False
            elif(event.type == pygame.MOUSEBUTTONUP):
                if(event.button == 1):
                    drag = False
                    scroll = False
                    renaming = False
            elif(event.type == pygame.MOUSEMOTION):
                if(drag):
                    mouse_x, mouse_y = event.pos
                    node1[1].x = mouse_x + dx
                    node1[1].y = mouse_y + dy
                if(scroll):
                    mouse_x, mouse_y = event.pos
                    for i in range(len(nodes)):
                        nodes[i][1].x = mouse_x + dxs[i]
                        nodes[i][1].y = mouse_y + dys[i]
            elif(event.type == pygame.MOUSEWHEEL):
                changeZoom(pygame.mouse.get_pos(), event.y)
        surface.fill(COLOUR_BG)
        for node_a in nodes:
            for node_b in nodes:
                colour = COLOUR_SELECTED if(selected in [node_a, node_b]) else COLOUR_FG
                pygame.draw.line(surface, colour, node_a[1].center, node_b[1].center, line_width * edges[nodes.index(node_a)][nodes.index(node_b)])
        for node in nodes: #looks nicer with nodes on top of edges
            colour = COLOUR_SELECTED if(node == selected) else COLOUR_FG
            pygame.draw.rect(surface, colour, pygame.Rect(node[1].x - 1, node[1].y - 1, node[1].w + 2, node[1].h + 2))
            surface.blit(node[0], node[1])
        if(file_menu):
            for item in menu:
                pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(item[1].x - 1, item[1].y - 1, item[1].w + 2, item[1].h + 2))
                surface.blit(item[0], item[1])
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    sys.exit()

# TODO
# Select multiple nodes (holding shift or control)
# Ability to colour nodes (change selected node to flashing or colour-changing)
# Change it so zooming and moving don't move the nodes, but the camera
# Vim-like
# Rules for connecting edges
# Edge names
# Edge weights?
# Digraph?
