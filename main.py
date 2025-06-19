import subprocess as sp
sp.run("pip install --upgrade --user pyglet")
import pyglet
from pyglet import shapes
from pyglet.window import key
import random
import time
import math
import tkinter as tk

root = tk.Tk()
root.withdraw() 
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.destroy()
window = pyglet.window.Window(width=width, height=height, caption='Map', style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
keys = []

dtexts = [
    pyglet.text.Label("Press ESC to exit", 0 , 0,color=(255,0,0)),
    pyglet.text.Label("Press SHIFT to sprint", 0 , 20,color=(255,0,0)),
    pyglet.text.Label("Press Q to toggle window focus", 0 , 40,color=(255,0,0)),
    pyglet.text.Label("Press R to regenerate the map", 0 , 60,color=(255,0,0)),
    pyglet.text.Label("Press M to see the map", 0 , 80,color=(255,0,0)),
]

m_mode = False
drawMap = False
SENS = 82

FOV = 80
RAYS = 100
RAYCAST_RES = 0.01 #The Smaller the more time it takes to render (raycast) but the less chance for rays to skip walls (0.01 is recommended)
theta = FOV/RAYS
print(theta)

MAP = []
D_MAP = []
MAP_SIZE = 10
TILE_SIZE = int(width/MAP_SIZE)
TSY = int(height/MAP_SIZE)

P_RAD = 10
DEFAULT_ANGLE = 45
p_speed = 1
x = y = TILE_SIZE
angle = DEFAULT_ANGLE

cyc = 0
draw_times = []
def generateMap():
    t1 = time.time()
    for y in range(MAP_SIZE):
        MAP.append(["" for i in range(MAP_SIZE)])
        D_MAP.append([None for i in range(MAP_SIZE)])
        for x in range(MAP_SIZE):
            if random.randint(1,100) % 2 == 0 and y != 1 and x != 1:
                MAP[y][x] = "#"
                D_MAP[y][x] = shapes.Rectangle(x*TILE_SIZE, y*TSY, (x*TILE_SIZE)+TILE_SIZE, (y*TSY)+TSY, color=(0, 0, 0))
            else:
                D_MAP[y][x] = shapes.Rectangle(x*TILE_SIZE, y*TSY, (x*TILE_SIZE)+TILE_SIZE, (y*TSY)+TSY, color=(255,255,255))
    print(f"Map Gen Time: {time.time()-t1}")

def reset():
    global x,y,angle
    x = y = TILE_SIZE
    angle = DEFAULT_ANGLE
    generateMap()

def calcPlayerMove():
    mx = 0
    my = 0
    for k in keys:
        if k == key.A:
            nx = (p_speed*math.cos(math.radians((90+angle))))
            ny = (p_speed*math.sin(math.radians((90+angle))))
        elif k == key.D:
            nx = (-p_speed*math.cos(math.radians((90+angle))))
            ny = (-p_speed*math.sin(math.radians((90+angle))))
        elif k == key.W:
            nx = (p_speed*math.cos(math.radians(angle)))
            ny = (p_speed*math.sin(math.radians(angle)))
        elif k == key.S:
            nx = (-p_speed*(math.cos(math.radians(angle))))
            ny = (-p_speed*(math.sin(math.radians(angle))))
        mx += nx
        my += ny
    return mx,my

def Raycast(x,y,angle):
    global width
    dx = math.cos(math.radians(angle)) * TILE_SIZE
    dy = math.sin(math.radians(angle)) * TSY
    tx = x;ty = y;hit = False
    while not hit:
        tx+= dx * 0.01;ty+= dy * 0.01
        try:
            if MAP[math.floor(ty/TSY)][math.floor(tx/TILE_SIZE)] == "#": hit = True
        except:pass
        if math.floor(tx) not in range(0,width+1) or math.floor(ty) not in range(0,height+1):break
    if tx != x or ty != y:
        return (math.floor(tx/TILE_SIZE),math.floor(ty/TSY)),(tx,ty), math.sqrt(((tx-x)**2)+((ty-y)**2))
    else:
        return 0,0,0
    
@window.event
def on_key_press(symbol, modifiers):
    global m_mode,drawMap,p_speed
    if symbol in [key.W,key.A,key.S,key.D] and m_mode:keys.append(symbol)
    if symbol == key.M and m_mode:
        drawMap = True if drawMap == False else False
    if symbol == key.LSHIFT:p_speed = 2
    if symbol == key.R:reset()
    if symbol == key.Q:
        m_mode = True if m_mode == False else False
        if m_mode == False:keys.clear();p_speed = 1
        window.set_exclusive_mouse(m_mode)

@window.event
def on_key_release(symbol, modifiers):
    global p_speed
    if symbol in [key.W,key.A,key.S,key.D] and m_mode:keys.remove(symbol)
    if symbol == key.LSHIFT:p_speed = 1

@window.event
def on_mouse_motion(x, y, dx, dy):
    global angle
    if m_mode:angle -= math.degrees(math.atan(dx/SENS))

@window.event
def on_draw():
    global x,y,cyc,draw_times,dtexts
    t1 = time.time()
    window.clear()
    mx,my = calcPlayerMove()
    mpx = math.floor(x/TILE_SIZE)
    mpy = math.floor(y/TSY)
    if 0+P_RAD <= x+mx <= width-P_RAD:
        if cyc >= 10:
            try:
                if MAP[mpy][math.floor((x+mx)/TILE_SIZE)] == "#":
                    #print("X collision")
                    if mpx > math.floor((x+mx)/TILE_SIZE):x = (((math.floor((x+mx)/TILE_SIZE))*TILE_SIZE)+TILE_SIZE)+(P_RAD/6)
                    else:x = ((math.floor((x+mx)/TILE_SIZE))*TILE_SIZE)-(P_RAD/6)
                else:x+=mx
            except:x+=mx
        elif mx > 0: cyc+=1
    if 0+P_RAD <= y+my <= height-P_RAD:
        if cyc >= 3:
            try:
                if MAP[math.floor((y+my)/TSY)][mpx] == "#":
                    #print("Y collision")
                    if mpy > math.floor((y+my)/TSY):y = (((math.floor((y+my)/TSY))*TSY)+TSY)+(P_RAD/6)
                    else:y = ((math.floor((y+my)/TSY))*TSY)-(P_RAD/6)
                else: y+=my
            except:y+=my
        elif mx > 0: cyc+=1
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
        len = abs(len * math.cos(math.radians(FOV)))
        if hmc != 0:
            hmc = "Border" if not hmc[0] in range(MAP_SIZE) or not hmc[1] in range(MAP_SIZE) else hmc
            #print(f"Ray #{i}: \n \tHit tile -> {hmc}\n \tRay Lenght -> {len}")
            if drawMap:
                shapes.Line(x,y, dmc[0], dmc[1], thickness=1,color=(0,0,255)).draw()
            else:
                lh = ((1/len)*height)
                ls = height/lh
                alh = (height/ls) * 12
                wcolor = math.floor(255 * ((len/ls)/(0.3*ls)))
                if hmc != "Border":
                    shapes.Rectangle(width-(width/RAYS)*(i+1),ls,width/RAYS,alh,color=(0,0,wcolor)).draw()
                else:
                    shapes.Rectangle(width-(width/RAYS)*(i+1),ls,width/RAYS,alh,color=(wcolor,wcolor,wcolor)).draw()
            t+=theta
    for e in dtexts:e.draw()
    draw_times.append(time.time()-t1)
    if draw_times.__len__() > 120:draw_times.pop(0)
    dts = 0
    for i in draw_times:dts+=i
    pyglet.text.Label(str(int(1/(dts/draw_times.__len__()))) + " FPS",0,height-20,color=(0,255,0)).draw()

generateMap()
pyglet.app.run()