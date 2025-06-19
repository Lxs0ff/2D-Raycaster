import subprocess as sp
sp.run("pip install --upgrade --user pyglet")
import pyglet
from pyglet import shapes
from pyglet.window import key
import random
import time
import math

width = 800
window = pyglet.window.Window(width=width, height=width, caption='Map')
keys = []

m_mode = False
drawMap = True
SENS = 82

FOV = 80
RAYS = 100
RAYCAST_RES = 0.01 #The Smaller the more time it takes to render but the less chance for rays to skip walls (0.01 is recommended)
theta = FOV/RAYS
print(theta)

MAP = []
D_MAP = []
MAP_SIZE = 10
TILE_SIZE = width/MAP_SIZE

P_RAD = 10
P_SPEED = 1
x = y = TILE_SIZE/2
angle = 90

t1 = time.time()
for y in range(MAP_SIZE):
    MAP.append(["" for i in range(MAP_SIZE)])
    D_MAP.append([None for i in range(MAP_SIZE)])
    for x in range(MAP_SIZE):
        if random.randint(1,100) % 2 == 0 and y != 0 and x != 0:
            MAP[y][x] = "#"
            D_MAP[y][x] = shapes.Rectangle(x*TILE_SIZE, y*TILE_SIZE, (x*TILE_SIZE)+TILE_SIZE, (y*TILE_SIZE)+TILE_SIZE, color=(0, 0, 0))
        else:
            D_MAP[y][x] = shapes.Rectangle(x*TILE_SIZE, y*TILE_SIZE, (x*TILE_SIZE)+TILE_SIZE, (y*TILE_SIZE)+TILE_SIZE, color=(255,255,255))
print(f"Map Gen Time: {time.time()-t1}")

def calcPlayerMove():
    mx = 0
    my = 0
    for k in keys:
        if k == key.A:
            nx = (P_SPEED*math.cos(math.radians((90+angle))))
            ny = (P_SPEED*math.sin(math.radians((90+angle))))
        elif k == key.D:
            nx = (-P_SPEED*math.cos(math.radians((90+angle))))
            ny = (-P_SPEED*math.sin(math.radians((90+angle))))
        elif k == key.W:
            nx = (P_SPEED*math.cos(math.radians(angle)))
            ny = (P_SPEED*math.sin(math.radians(angle)))
        elif k == key.S:
            nx = (-P_SPEED*(math.cos(math.radians(angle))))
            ny = (-P_SPEED*(math.sin(math.radians(angle))))
        mx += nx
        my += ny
    return mx,my

def Raycast(x,y,angle):
    global width
    dx = math.cos(math.radians(angle)) * TILE_SIZE
    dy = math.sin(math.radians(angle)) * TILE_SIZE
    tx = x;ty = y;hit = False
    while not hit:
        tx+= dx * 0.01;ty+= dy * 0.01
        try:
            if MAP[math.floor(ty/TILE_SIZE)][math.floor(tx/TILE_SIZE)] == "#": hit = True
        except:pass
        if math.floor(tx) not in range(0,width+1) or math.floor(ty) not in range(0,width+1):break
    if tx != x or ty != y:
        return (math.floor(tx/TILE_SIZE),math.floor(ty/TILE_SIZE)),(tx,ty), math.sqrt(((tx-x)**2)+((ty-y)**2)) if math.sqrt((((tx-x)**2)+((ty-y)**2))) <= width else width
    else:
        return 0,0,0
    
@window.event
def on_key_press(symbol, modifiers):
    global m_mode,drawMap
    if symbol in [key.W,key.A,key.S,key.D] and m_mode:keys.append(symbol)
    if symbol == key.M and m_mode:
        drawMap = True if drawMap == False else False
    if symbol == key.Q:
        m_mode = True if m_mode == False else False
        if m_mode == False:keys.clear()
        window.set_exclusive_mouse(m_mode)

@window.event
def on_key_release(symbol, modifiers):
    if symbol in [key.W,key.A,key.S,key.D] and m_mode:keys.remove(symbol)

@window.event
def on_mouse_motion(x, y, dx, dy):
    global angle
    if m_mode:angle -= math.degrees(math.atan(dx/SENS))

@window.event
def on_draw():
    global x,y
    #t1 = time.time()
    window.clear()
    mx,my = calcPlayerMove()
    mpx = math.floor(x/TILE_SIZE)
    mpy = math.floor(y/TILE_SIZE)
    if 0+P_RAD <= x+mx <= width-P_RAD:
        try:
            if MAP[mpy][math.floor((x+mx)/TILE_SIZE)] == "#":
                print("X collision")
                if mpx > math.floor((x+mx)/TILE_SIZE):x = (((math.floor((x+mx)/TILE_SIZE))*TILE_SIZE)+TILE_SIZE)+(P_RAD/6)
                else:x = ((math.floor((x+mx)/TILE_SIZE))*TILE_SIZE)-P_RAD/6
            else:x+=mx
        except:x+=mx
    if 0+P_RAD <= y+my <= width-P_RAD:
        try:
            if MAP[math.floor((y+my)/TILE_SIZE)][mpx] == "#":
                print("Y collision")
                if mpy > math.floor((y+my)/TILE_SIZE):y = (((math.floor((y+my)/TILE_SIZE))*TILE_SIZE)+TILE_SIZE)+(P_RAD/6)
                else:y = ((math.floor((y+my)/TILE_SIZE))*TILE_SIZE)-P_RAD/6
            else: y+=my
        except:y+=my
    if drawMap:
        for ly in range(MAP_SIZE):
            for lx in range(MAP_SIZE):
                D_MAP[ly][lx].draw()
        shapes.Circle(x,y,P_RAD/2,color=(0,255,0)).draw()
        shapes.Line(x,y, x+(P_RAD/1.5*math.cos(math.radians(angle))), y+(P_RAD/1.5*math.sin(math.radians(angle))), thickness=1,color=(255,0,0)).draw()
    else:
        pass
    t = -((RAYS/2)*theta) + angle
    for i in range(RAYS):
        hmc,dmc,len = Raycast(x,y,t)
        len = abs(len * math.cos(FOV))
        if hmc != 0:
            hmc = "Border" if not hmc[0] in range(MAP_SIZE) or not hmc[1] in range(MAP_SIZE) else hmc
            #print(f"Ray #{i}: \n \tHit tile -> {hmc}\n \tRay Lenght -> {len}")
            if drawMap:
                shapes.Line(x,y, dmc[0], dmc[1], thickness=1,color=(0,0,255)).draw()
            else:
                h = (1/len*width)*5
                lh = int(h/len)
                if hmc != "Border":
                    shapes.Rectangle(width-(width/RAYS)*(i+1),lh/2,width/RAYS,lh+h,color=(0,0,255)).draw()
                else:
                    shapes.Rectangle(width-(width/RAYS)*(i+1),lh/2,width/RAYS,lh+h,color=(255,0,0)).draw()
            t+=theta
    #print(f"Draw Time: {time.time()-t1}")

pyglet.app.run()


