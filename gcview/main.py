from __future__ import division #Necessary for some people that still use 2.5, can't hurt
import sys
import re

import pyglet
from pyglet.gl import *

import parse
import draw
import state

#Zoom level
gzl = 1

#Maps G-Codes to python functions
fdict = {
   'G00' : draw.rapid,
   'G01' : draw.lerp,
   'G20' : state.set_imperial,
   'G21' : state.set_metric,
   'G90' : state.set_absolute,
   'G91' : state.set_incremental
}

def add_dict(d1, d2):
    #TODO: Take more then one dict(In one line)
    return dict(d1.items() + d2.items())

def start_display_list():
    dlist = glGenLists(1)
    glNewList(dlist, GL_COMPILE)
    
    return dlist

def interpret_file(lines, fdict):
    '''
    This function acts like the main loop.  It has side effects.  Unfortunately this program sorta lends itself to those.  Or it might just be that i'm not a real programmer.  Likely the latter.
    '''
    statedict = {'absolute' : True, 'inches' : True}
    args = {'X':0, 'Y':0, 'Z':0, 'SD' : statedict}
    for l in lines:
        #The 'e' represents the args and predicate from the expression
        epred, eargs = parse.line(l)
        args['OX'], args['OY'], args['OZ'], args['OC'] = args['X'], args['Y'], args['Z'], [epred, eargs]
        args = add_dict(args, eargs)
        if not statedict['absolute']:
            #If incremental
            for x in ['X', 'Y', 'Z']:
                args[c] += args['O' + c]
        if epred in fdict.keys():
            fdict[epred](args)
        else:
            #This is just so I know what to implement
            if '-v' in sys.argv:
                print epred
            
           
    return statedict

def on_mouse_drag(x, y, dx, dy, buttons, mods):
    global gzl
    if buttons == 1:
        #For panning
        glTranslatef(dx*(gzl**-1), dy*(gzl**-1), 0)
    if buttons == 4:
        #Rotation.  Not sure why, maybe desirable in some obscure instances.
        glTranslatef(x, y, 0)
        glRotatef(dx, 0, 0, 1)
        glTranslatef(-x, -y, 0)

#TODO: Make this function do something
def on_mouse_scroll(x, y, dx, dy):
    #This will have to be a translation or a scale on the OpenGL Level
    #as we calculate all the graphics at the beginning of the program
    global gzl #This is only a global variable so we can multiply panning, to make it work on a 1:1 ratio at all zoom levels
    zl = 1 + (dy/10)
    gzl *= zl
    if '-Z' not in sys.argv:
        print 'Zoom Level: ' + str(gzl)
    #Translate to the mouse so we don't zoom about the origin
    glTranslatef(x, y, 0)
    glScalef(zl, zl, zl)
    glTranslatef(-x, -y, 0)


def on_draw(t, win, dlist):
    win.clear()

    glCallList(dlist)
    
    win.flip()

if __name__ == '__main__':
    #Get a G-Code file
    file = open(sys.argv[1])
    inp = file.read()

    nc = filter(lambda x: x != '', parse.remove_comments(inp).split('\n'))
    
    #Generate a display list
    dlist = start_display_list()
    glBegin(GL_LINE_STRIP)
    statedict = interpret_file(nc, fdict)
    glEnd()
    glEndList()

    print 'Coordinates: ' + {True:'Absolute', False:'Incremental'}[statedict['absolute']]
    print 'Units: ' + {True:'Imperial', False:'Metric'}[statedict['inches']]

    win = pyglet.window.Window(800, 800)

    win.on_mouse_drag = on_mouse_drag
    win.on_mouse_scroll = on_mouse_scroll

    pyglet.clock.schedule(on_draw, win, dlist)
    pyglet.app.run()
