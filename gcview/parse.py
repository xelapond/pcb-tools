import re

#Regex for finding a G-Code comment
fc = re.compile('\(.*\)')

#Return a list of all the comments(as strings)
fci = lambda t: fc.findall(t)

def remove_comments(t):
    comments = fci(t)
    for c in comments:
        t = ''.join(t.split(c))

    return t

def args2dict(args):
    '''
    Converts a G-Code argument list into a dictionary

    Example:
       ['X1.010', 'Y0.045'] -> {'X':1.010, 'Y':0.045}
    '''
    return dict((exp[:1], float(exp[1:])) for exp in args)

def line(line):
    #TODO: Implement multiple commands per line
    #Do this in one of two ways
    #   Hackish: Split by G, use list comprehension and add the G back, then recurse
    #   Not So Hackish: Write a function to split based on a regex
    #/TODO
    exp = line.split(' ')
    try:
        exp.remove('')
    except:
        pass

    pred = exp[0]
    args = args2dict(exp[1:])
    return pred, args
