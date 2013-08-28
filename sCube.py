import pygame as pg
from pygame.locals import *
import math as mt

colors = [(255,255,255),(255,0,0),(0,200,0),(247,100,30),(0,0,255),(247,221,43)] # white,red,green,orange,blue,yellow

pg.init()
pg.key.set_repeat(100,10)

surf = pg.display.set_mode((350,350),RESIZABLE)

CX = 0 # center of cube and screen
CY = 0 # center of cube and screen
S =  0 # half of the edges' length

FOCAL = 10 # focal length, used for perspective

F_DOWN  = [[-1,1,1], [1,1,1],   [1,1,-1],  [-1,1,-1]]
F_FACE  = [[-1,1,1], [1,1,1],   [1,-1,1],  [-1,-1,1]]
F_RIGHT = [[1,1,1] , [1,-1,1],  [1,-1,-1], [1,1,-1]]
F_BACK  = [[1,1,-1], [1,-1,-1], [-1,-1,-1],[-1,1,-1]]
F_LEFT  = [[-1,1,-1],[-1,-1,-1],[-1,-1,1], [-1,1,1]]
F_UP    = [[-1,-1,1],[1,-1,1],  [1,-1,-1], [-1,-1,-1]]
CUBE = [F_DOWN,F_FACE,F_RIGHT,F_BACK,F_LEFT,F_UP] # listes des faces, chaque face étant une liste de ses points. La face cube[n] étant colors[n]

def rotate(a,b): # return CUBE after a rotation of a° around x and b° around y
    global CUBE
    a=mt.radians(a)
    b=mt.radians(b)
    newC=[]
    newF=[]
    p=[]
    for face in CUBE:
        newF=[]
        for point in face:
            p=[point[0],point[1]*mt.cos(a)-point[2]*mt.sin(a),point[1]*mt.sin(a)+point[2]*mt.cos(a)]
            p=[p[2]*mt.sin(b)+p[0]*mt.cos(b),p[1],p[2]*mt.cos(b)-p[0]*mt.sin(b)]
            newF.append(p)
        newC.append(newF)
    CUBE = newC
    return newC

def persp(c): # return cube asuming perspective, watching along z
    newC=[]
    newF=[]
    p=[]
    for face in c:
        newF=[]
        for point in face:
            p=[point[0]*(1+point[2]/FOCAL),point[1]*(1+point[2]/FOCAL),point[2]]
            newF.append(p)
        newC.append(newF)
    return newC

def draw(c): # draw cube on surf
    poly=[] # liste des faces à dessiner, en tuples (zAvrg,[points],color)
    for i in range(6):
        poly.append((zAvrg(c[i]),[[p[0]*S+CX,p[1]*S+CY] for p in c[i]],i))
    poly.sort()
    surf.fill((0,0,0))
    for (_,points,i) in poly:
        pg.draw.polygon(surf,colors[i],points)
    pg.display.flip()

def zAvrg(f): #retourne le z moyen d'une face
    return (f[0][2]+f[1][2]+f[2][2]+f[3][2])/4

def fitCube(w,h):
    global CX, CY, S
    CX=w/2
    CY=h/2
    S=(min(w,h)-10)/(2*mt.sqrt(3))
    draw(persp(CUBE))

def motion(k):
    a=0
    b=0
    if k[K_UP]:
        a+=2
    if k[K_DOWN]:
        a-=2
    if k[K_LEFT]:
        b-=2
    if k[K_RIGHT]:
        b+=2
    rotate(a,b)
    draw(persp(CUBE))

fitCube(350,350)

ok = True
while ok:
    for evt in pg.event.get():
        if evt.type == QUIT:
            ok = False
        elif evt.type == KEYDOWN:
            motion(pg.key.get_pressed())
        elif evt.type == MOUSEMOTION and evt.buttons[0]==1:
            rotate(-evt.rel[1]/2.5,evt.rel[0]/2.5)
            draw(persp(CUBE))
        elif evt.type == VIDEORESIZE:
            fitCube(evt.w,evt.h)