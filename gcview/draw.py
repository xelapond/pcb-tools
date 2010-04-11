from pyglet.gl import *

from constants import *

def vertex(args):
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
    
def rapid(args):
    #We just do this so we don't get blending
    if args['OC'][0] == 'GO1':
        glEnd()
        glBegin(GL_LINE_STRIP)

    glColor4f(*RAPID_POS_COLOR)

    return vertex(args)

def lerp(args):
    #We just do this so we don't get blending
    if args['OC'][0] == 'GO1':
        glEnd()
        glBegin(GL_LINE_STRIP)

    glColor4f(*LERP_COLOR)

    return vertex(args)
