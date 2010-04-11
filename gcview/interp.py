import parse
import utils

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
        args = utils.add_dict(args, eargs)
        if not statedict['absolute']:
            #If incremental
            for x in ['X', 'Y', 'Z']:
                args[c] += args['O' + c]
        if epred in fdict.keys():
            fdict[epred](args)
        else:
            #This is just so I know what to implement
            print epred
            
           
    return statedict
