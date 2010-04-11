from __future__ import division #Necessary for some people that still use 2.5, can't hurt
import sys
import re

import pyglet
from pyglet.gl import *

import parse

#Zoom level
gzl = 1

LERP_COLOR = (1, 1, 1, 1)
RAPID_POS_COLOR = (1, 0, 0, 0)

#I Think this is depreciated, but maybe not
#We'll see
cdict = {
    .5  : (1, 0, 0), 
    .02 : (0, 0, 0),

     'EXCEPTION' : (1, 1, 1)
}

def draw_vertex(args):
    k = args.keys()
    '''
    Lots of stuff happens here.
    I don't want to explain how this works, it was too much fun to write.
    That would ruin the fun.
    
    What this does is see if there is an X, Y and Z coordinate.  
    It puts them in a list; [X, Y, Z].
    If any of them are missing, it checks for an old coordinate(from the last command(OX, OY or OZ).
    If there is one present, it uses that.
    If neither the current coordinate or its old counterpart exist, use the name of the coordinate(sans 'O')
    If there are any strings in the list(meaning there was a missing coordinate) it can't be drawn
    '''
    #p = [not (type(g) == str) or ('O' + g) in k for g in 
    #p = [((not (g[0] == 'O') and args[g])) or ((g in k) and args[g]) or (g[1]) for g in [((x in k) and x) or ('O' + x) for x in ['X', 'Y', 'Z']]]
    p = ['X', 'Y', 'Z']
    for cn in p:
        if cn in k:
            p[p.index(cn)] = args[cn]
        else:
            if 'O' + cn in k:
                p[p.index(cn)] = args['O' + cn]

    t = filter(lambda x: type(x) == str, p)
    if t:
        print 'Could not execute command, no ' + str(t) + ' Coordinate(s)'
        return False, p

    glVertex2f(p[0]*400, p[1]*400)
    return True
    
def draw_rapid(args):
    #We just do this so we don't get blending
    if args['OC'][0] == 'GO1':
        glEnd()
        glBegin(GL_LINE_STRIP)

    glColor4f(*RAPID_POS_COLOR)

    return draw_vertex(args)

def draw_lerp(args):
    #We just do this so we don't get blending
    if args['OC'][0] == 'GO1':
        glEnd()
        glBegin(GL_LINE_STRIP)

    glColor4f(*LERP_COLOR)

    return draw_vertex(args)

def set_imperial(args):
    args['SD']['inches'] = True

def set_metric(args):
    args['SD']['inches'] = False

def set_absolute(args):
    args['SD']['absolute'] = True

def set_incremental(args):
    args['SD']['absolute'] = False

#Maps G-Codes to python functions
fdict = {
   'G00' : draw_rapid,
   'G01' : draw_lerp,
   'G20' : set_imperial,
   'G21' : set_metric,
   'G90' : set_absolute,
   'G91' : set_incremental
}

def add_dict(d1, d2):
    #TODO: Take more then one dict(In one line)
    return dict(d1.items() + d2.items())

def start_display_list():
    dlist = glGenLists(1)
    glNewList(dlist, GL_COMPILE)
    
    return dlist

def args2dict(args):
    '''
    Converts a G-Code argument list into a dictionary

    Example:
       ['X1.010', 'Y0.045'] -> {'X':1.010, 'Y':0.045}
    '''
    return dict((exp[:1], float(exp[1:])) for exp in args)

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
