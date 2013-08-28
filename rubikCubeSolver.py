import pygame as pg
from pygame.locals import *
import math as mt
import time
import copy
import random

BLA=(0,0,0)
WHI=(255,255,255)
RED=(255,0,0)
GRE=(0,200,0)
ORA=(247,100,30)
BLU=(0,0,255)
YEL=(247,221,43)

CX=175
CY=175
S=100
FOCAL=10

class Point:
    """define a point in space with 3 coponents x, y & z"""

    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z

    def rotateX(self,a):
        """rotation of a° around x axis"""
        a=mt.radians(a)
        (self.y , self.z) = (self.y * mt.cos(a) - self.z * mt.sin(a) , self.y * mt.sin(a) + self.z * mt.cos(a))
        return self

    def rotateY(self,b):
        """rotation of b° around y axis"""
        b=mt.radians(b)
        (self.x , self.z) = (self.z * mt.sin(b) + self.x * mt.cos(b) , self.z * mt.cos(b) - self.x * mt.sin(b))
        return self

    def rotateXY(self,a,b):
        """rotation of a° around x axis and b° around y axis"""
        return self.rotateX(a).rotateY(b)

    def project(self):
        """return the 2 dimensions of the Point after projection on x-y plan, assuming perspective"""
        return [self.x*(1+self.z/FOCAL)*S+CX , self.y*(1+self.z/FOCAL)*S+CY]

class Face:
    """define a square face with four corners and a color"""

    def __init__(self,corners,color):
        self.corners = corners
        self.color = color

    def __lt__(self,other):
        return self.zAvrg() < other.zAvrg()

    def center(self):
        """return the center Point of a Face"""
        pa=self.corners[0]
        pb=self.corners[2]
        return Point((pa.x+pb.x)/2 , (pa.y+pb.y)/2 , (pa.z+pb.z)/2)

    def zAvrg(self):
        """return the z average of Face"""
        return sum([p.z for p in self.corners])/4

    def rotateXY(self,a,b):
        self.corners = [p.rotateXY(a,b) for p in self.corners]
        return self

    def project(self):
        return [p.project() for p in self.corners]

    def draw(self,surf):
        pg.draw.polygon(surf,self.color,self.project())
        pg.draw.polygon(surf,BLA,self.project(),3)

class RubikCube:
    """define a rubikCube as 54 Faces setted in 6 layers, 12 edges and 8 corners."""

    def __init__(self):
        self.faces=[]
        self.layer=[[],[],[],[],[],[]]#L R U D B F
        colors=[BLU,GRE,YEL,WHI,ORA,RED]
        r=-1
        for f in range(6):
            c = -1 if f % 2 == 0 else 1
            for i in range(3):
                b = i * 2/3 - 1
                for j in range(3):
                    a = j * 2/3 - 1
                    r+=1
                    if f in range(2):
                        self.faces.append(Face([Point(c,a,b),Point(c,a+2/3,b),Point(c,a+2/3,b+2/3),Point(c,a,b+2/3)],colors[f]))
                    elif f in range(2,4):
                        self.faces.append(Face([Point(b,c,a),Point(b,c,a+2/3),Point(b+2/3,c,a+2/3),Point(b+2/3,c,a)],colors[f]))
                    else:
                        self.faces.append(Face([Point(a,b,c),Point(a+2/3,b,c),Point(a+2/3,b+2/3,c),Point(a,b+2/3,c)],colors[f]))
                    self.layer[f].append(r)
        self.layer[0]+=[42,39,36,29,28,27,45,48,51,18,19,20]
        self.layer[1]+=[26,25,24,38,41,44,33,34,35,53,50,47]
        self.layer[2]+=[0 ,3 ,6 ,45,46,47,15,12,9 ,38,37,36]
        self.layer[3]+=[42,43,44,8 ,5 ,2 ,53,52,51,11,14,17]
        self.layer[4]+=[27,30,33,0 ,1 ,2 ,24,21,18,11,10,9 ]
        self.layer[5]+=[20,23,26,15,16,17,35,32,29,8 ,7 ,6 ]
        self.edge=[(32,52),(34,14),(30,43),(28, 5),( 7,48),(50,16), #from bottom, F, trigonometric wise from U and D
                   (10,41),(39, 1),(23,46),(25,12),(21,37),(19, 3)]
        self.corner=[(29, 8,51),(35,53,17),(33,11,44),(27,42, 2),
                     (20, 6,45),(26,47,15),(24, 9,38),(18,36, 0)]
        self.rotateXY(0,-40)
        self.rotateXY(-26,0)

    def draw(self,surf):
        faces=list(self.faces)
        faces.sort()
        for face in faces:
            face.draw(surf)

    def rotateXY(self,a,b):
        self.faces=[f.rotateXY(a,b) for f in self.faces]
    
    def rotateLayer(self,l,d,surf):
        """Rotation of the l layer, clockwise if d=1, counterclockwise if d=-1"""
        def liRot(l,n):
            return l[n:]+l[:n]
        sl = self.layer[l]
        sf_old=copy.deepcopy(self.faces)
        u = self.faces[sl[4]].center() #rotation of layer around u
        a=mt.radians(3*d) #1° between two positions
        d = d if l%2==0 else -d
        c=mt.cos(a)
        s=mt.sin(a)
        R=[[u.x**2+c*(1-u.x**2) , u.x*u.y*(1-c)-u.z*s , u.x*u.z*(1-c)+u.y*s],
           [u.x*u.y*(1-c)+u.z*s , u.y**2+c*(1-u.y**2) , u.y*u.z*(1-c)-u.x*s],
           [u.x*u.z*(1-c)-u.y*s , u.y*u.z*(1-c)+u.x*s , u.z**2+c*(1-u.z**2)]] # rotation matrix
        for i in range(30):
            for f in sl:
                self.faces[f].corners=[Point(p.x*R[0][0]+p.y*R[0][1]+p.z*R[0][2],
                                             p.x*R[1][0]+p.y*R[1][1]+p.z*R[1][2],
                                             p.x*R[2][0]+p.y*R[2][1]+p.z*R[2][2]) for p in self.faces[f].corners]
            surf.fill(BLA)
            self.draw(surf)
            pg.display.flip()
            time.sleep(0.001)
        self.faces=sf_old
        lis=[[0,2,8,6],[1,5,7,3]]+[[3*(i+3)+j for i in range(4)] for j in range(3)]
        for li in lis:
            newC = list([self.faces[sl[j]].color for j in liRot(li,d)])
            for i,j in enumerate(li):
                self.faces[sl[j]].color = newC[i]
    
    def moves(self,li,surf):
        """A few layers rotations are applied. li is list of (layer,direction)."""
        for l,d in li:
            self.rotateLayer(l,d,surf)
    
    def scramble(self,surf):
        """Mix the cube randomly"""
        l_old=-1
        for i in range(24):
            l=random.randrange(0,6)
            while l==l_old:
                l=random.randrange(0,6)
            l_old=l
            self.rotateLayer(l,random.randrange(-1,2,2),surf)
    
    def solve(self,surf):
        """Solve the cube"""
        e=self.edge
        c=self.corner
        lay=[5,1,4,0]
        liMoves = []
        
        #-----cross-----
        for ed in range(4):
            r=lambda x:(x+ed)%4
            edCol = [RED,GRE,ORA,BLU][ed]
            for n,fs in enumerate(e[:4]): #DOWN layer
                liMoves=[]
                fa,fb=fs
                if self.faces[fa].color in [WHI,edCol] and self.faces[fb].color in [WHI,edCol]:
                    if n==r(1) or n==r(2): liMoves+=[(lay[n],1)]
                    if n==r(3) or (n==r(0) and self.faces[fb].color==WHI): liMoves+=[(lay[n],-1)]
                self.moves(liMoves,surf)
            for n,fs in enumerate(e[4:8]): #MID layer
                liMoves=[]
                fa,fb=fs
                if self.faces[fa].color in [WHI,edCol] and self.faces[fb].color in [WHI,edCol]:
                    d=1
                    f=-1
                    if self.faces[fb].color == WHI:
                        if n==r(1) or n==r(3): d=-1
                        f=1
                        n=(n-1)%4
                    if n==r(0): liMoves+=[(lay[n],-d)]
                    elif n==r(1): liMoves+=[(3,d),(lay[n],f),(3,-d)]
                    elif n==r(2): liMoves+=[(3,d)]*2+[(lay[n],-d)]+[(3,-d)]*2
                    else: liMoves+=[(3,-d),(lay[n],f),(3,d)]
                self.moves(liMoves,surf)
            for n,fs in enumerate(e[8:]):  #UP layer
                liMoves=[]
                fa,fb=fs
                if self.faces[fa].color == WHI and self.faces[fb].color == edCol: #white in UP
                    if n==r(2): liMoves+=[(2,1)]*2
                    elif n==r(3): liMoves+=[(2,-1)]
                    elif n==r(1): liMoves+=[(2,1)]
                    liMoves+=[(lay[ed],1)]*2
                if self.faces[fb].color == WHI and self.faces[fa].color == edCol: #white not in UP
                    if n==r(0): liMoves+=[(2,-1)]
                    elif n==r(2): liMoves+=[(2,1)]
                    if n==r(3): liMoves+=[(lay[n],1),(lay[ed],-1),(lay[n],-1)]
                    else: liMoves+=[(lay[r(1)],-1),(lay[ed],1),(lay[r(1)],1)]
                self.moves(liMoves,surf)
        
        #-----Corners-----
        for co in range(4):
            r=lambda x:(x+co)%4
            coCol1=[RED,GRE,ORA,BLU][co-1]
            coCol2=[RED,GRE,ORA,BLU][co]
            cols = [WHI,coCol1,coCol2]
            for n,fs in enumerate(c[:4]):
                liMoves=[]
                fa,fb,fc = fs
                if self.faces[fa].color in cols and self.faces[fb].color in cols and self.faces[fc].color in cols:
                    if n!=r(0) or self.faces[fa].color!=WHI:
                        liMoves+=[(lay[n],1),(2,1),(lay[n],-1)]
                self.moves(liMoves,surf)
            for n,fs in enumerate(c[4:]):
                liMoves=[]
                fa,fb,fc = fs
                if self.faces[fa].color in cols and self.faces[fb].color in cols and self.faces[fc].color in cols:
                    if n==r(1): liMoves+=[(2,1)]
                    elif n==r(2): liMoves+=[(2,1)]*2
                    elif n==r(3): liMoves+=[(2,-1)]
                    n=r(0)
                    if self.faces[fa].color==WHI: liMoves+=[(lay[n],1),(2,-1),(lay[n],-1),(2,1),(2,1),(lay[n],1),(2,1),(lay[n],-1)]
                    elif self.faces[fb].color==WHI: liMoves+=[(lay[n-1],-1),(2,-1),(lay[n-1],1)]
                    elif self.faces[fc].color==WHI: liMoves+=[(lay[n],1),(2,1),(lay[n],-1)]
                self.moves(liMoves,surf)
        
        #-----Mid layer-----
        for ed in range(4):
            r=lambda x:(x+ed)%4
            edCol1=[RED,GRE,ORA,BLU][ed-1]
            edCol2=[RED,GRE,ORA,BLU][ed]
            for n,fs in enumerate(e[4:8]):
                liMoves=[]
                fa,fb = fs
                if self.faces[fa].color in [edCol1,edCol2] and self.faces[fb].color in [edCol1,edCol2]:
                    if n!=r(0) or self.faces[fa].color!=edCol1:
                        liMoves+=[(lay[n],1),(2,1),(lay[n],-1),(2,-1),(lay[n-1],-1),(2,-1),(lay[n-1],1)]
                self.moves(liMoves,surf)
            for n,fs in enumerate(e[8:]):
                liMoves=[]
                fa,fb = fs
                if self.faces[fa].color in [edCol1,edCol2] and self.faces[fb].color in [edCol1,edCol2]:
                    if self.faces[fa].color == edCol1:
                        if n==r(0): liMoves+=[(2,-1)]
                        elif n==r(2): liMoves+=[(2,1)]
                        elif n==r(3): liMoves+=[(2,1)]*2
                        n=r(0)
                        liMoves+=[(lay[n-1],-1),(2,1),(lay[n-1],1),(lay[n],-1),(lay[n-1],1),(lay[n],1),(lay[n-1],-1)]
                    elif self.faces[fa].color == edCol2:
                        if n==r(0): liMoves+=[(2,1)]*2
                        elif n==r(1): liMoves+=[(2,-1)]
                        elif n==r(3): liMoves+=[(2,1)]
                        n=r(0)
                        liMoves+=[(lay[n],1),(2,-1),(lay[n],-1),(lay[n-1],1),(lay[n],-1),(lay[n-1],-1),(lay[n],1)]
                self.moves(liMoves,surf)
        
        #-----Edges orient last layer-----
        li=e[8:]
        for i in range(4):
            liMoves=[]
            l=li[i:]+li[:i]
            if [self.faces[l[k][0]].color == YEL for k in range(4)] == [False]*4:
                liMoves+=[(lay[i],1),(lay[(i+1)%4],1),(2,1),(lay[(i+1)%4],-1),(2,-1),(lay[i],-1)]
            elif [self.faces[l[k][0]].color == YEL for k in range(4)] == [False,True]*2:
                liMoves+=[(lay[i],1),(lay[(i+1)%4],1),(2,1),(lay[(i+1)%4],-1),(2,-1),(lay[i],-1)]
            elif [self.faces[l[k][0]].color == YEL for k in range(4)] == [False]*2+[True]*2:
                liMoves+=[(lay[i],1),(2,1),(lay[(i+1)%4],1),(2,-1),(lay[(i+1)%4],-1),(lay[i],-1)]
            self.moves(liMoves,surf)
            
        #-----Corners oll-----
        li=c[4:]
        U=(2,1)
        U_=(2,-1)
        for i in range(4):
            liMoves=[]
            l=li[i:]+li[:i]
            R=(lay[i-3],1)
            R_=(lay[i-3],-1)
            F=(lay[i],1)
            F_=(lay[i],-1)
            L=(lay[i-1],1)
            L_=(lay[i-1],-1)
            if [self.faces[l[k][j]].color == YEL for k,j in enumerate([1,1,2,2])] == [True]*4:
                liMoves+=[R,U,U,R_,R_,U_,R,R,U_,R,R,U,U,R]
            elif [self.faces[l[k][j]].color == YEL for k,j in enumerate([1,2,1,2])] == [True]*4:
                liMoves+=[R,U,R_,U,R,U_,R_,U,R,U,U,R_]
            elif [self.faces[l[k][j]].color == YEL for k,j in enumerate([0,1,1,1])] == [True]*4:
                liMoves+=[R,U,R_,U,R,U,U,R_]
            elif [self.faces[l[k][j]].color == YEL for k,j in enumerate([2,2,0,2])] == [True]*4:
                liMoves+=[R,U,U,R_,U_,R,U_,R_]
            elif [self.faces[l[k][j]].color == YEL for k,j in enumerate([2,1,0,0])] == [True]*4:
                liMoves+=[R,R,(3,1),R_,U,U,R,(3,-1),R_,U,U,R_]
            elif [self.faces[l[k][j]].color == YEL for k,j in enumerate([0,1,2,0])] == [True]*4:
                liMoves+=[R_,F_,L,F,R,F_,L_,F]
            elif [self.faces[l[k][j]].color == YEL for k,j in enumerate([1,0,2,0])] == [True]*4:
                liMoves+=[R_,F_,L_,F,R,F_,L,F]
            self.moves(liMoves,surf)
        
        #-----Corners Permut Last Layer-----
        for i in range(4):
            liMoves=[]
            l=li[i:]+li[:i]
            R=(lay[i-3],1)
            R_=(lay[i-3],-1)
            F=(lay[i],1)
            F_=(lay[i],-1)
            L=(lay[i-1],1)
            L_=(lay[i-1],-1)
            B=(lay[i-2],1)
            if self.faces[l[0][1]].color == self.faces[l[1][2]].color:
                if self.faces[l[1][1]].color == self.faces[l[2][2]].color:
                    liMoves+=[R_,F_,L_,F,R,F_,L,F,R_,F_,L,F,R,F_,L_,F]
                else:
                    liMoves+=[R_,F,R_,B,B,R,F_,R_,B,B,R,R]
                    break
        self.moves(liMoves,surf)
        col=self.faces[li[0][2]].color
        if col==GRE: self.rotateLayer(2,-1,surf)
        elif col==ORA:
            self.rotateLayer(2,1,surf)
            self.rotateLayer(2,1,surf)
        elif col==BLU: self.rotateLayer(2,1,surf)

        #-----Edges pll-----
        liCol=[RED,GRE,ORA,BLU]
        li=e[8:]
        for i in range(4):
            liMoves=[]
            l=li[i:]+li[:i]
            col=liCol[i:]+liCol[:i]
            R=(lay[i-3],1)
            R_=(lay[i-3],-1)
            F=(lay[i],1)
            F_=(lay[i],-1)
            L=(lay[i-1],1)
            L_=(lay[i-1],-1)
            if self.faces[l[1][1]] != col[1]:
                if self.faces[l[0][1]].color == col[2] and self.faces[l[1][1]].color == col[3]:
                    liMoves+=[L,L,R,R,(3,1),L,L,R,R,U,U,L,L,R,R,(3,1),L,L,R,R]
                elif self.faces[l[0][1]].color == col[0] and self.faces[l[3][1]].color == col[1]:
                    liMoves+=[R,R,U_,R_,U_,R,U,R,U,R,U_,R]
                elif self.faces[l[2][1]].color == col[2] and self.faces[l[3][1]].color == col[1]:
                    liMoves+=[R,R,U,R,U,R_,U_,R_,U_,R_,U,R_]
                elif self.faces[l[3][1]].color == col[0] and self.faces[l[1][1]].color == col[2]:
                    liMoves+=[R_,U_,R,U_,R,U,R,U_,R_,U,R,U,R,R,U_,R_,U,U]
                else: continue
                break
        self.moves(liMoves,surf)

def motion(k,rc,surf):
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
    rc.rotateXY(a,b)
    surf.fill(BLA)
    rc.draw(surf)
    pg.display.flip()

if __name__ == '__main__' :
    pg.init()
    pg.key.set_repeat(100,10)
    surf = pg.display.set_mode((350,350))
    rc=RubikCube()
    rc.draw(surf)
    pg.display.flip()
    pg.display.set_caption("Rubik's Cube solver")
    ok = True
    while ok:
        time.sleep(0.001)
        for evt in pg.event.get():
            if evt.type == QUIT:
                ok = False
            elif evt.type == KEYDOWN:
                kL=pg.key.get_pressed()
                k=evt.key
                d = -1 if kL[K_KP1] else 1
                if k == K_KP4:
                    rc.rotateLayer(0,d,surf)
                elif k == K_KP6:
                    rc.rotateLayer(1,d,surf)
                elif k == K_KP8:
                    rc.rotateLayer(2,d,surf)
                elif k == K_KP2:
                    rc.rotateLayer(3,d,surf)
                elif k == K_KP0:
                    rc.rotateLayer(4,d,surf)
                elif k == K_KP5:
                    rc.rotateLayer(5,d,surf)
                elif k == K_b:
                    rc.scramble(surf)
                elif k == K_s:
                    t0=time.perf_counter()
                    rc.solve(surf)
                    elapsed = "%.1f" % (time.perf_counter()-t0)
                    pg.display.set_caption("Rubik's Cube solver - "+elapsed+"s")
                motion(kL,rc,surf)
