from pyglet.gl import *

def start_display_list():
    dlist = glGenLists(1)
    glNewList(dlist, GL_COMPILE)
    
    return dlist

