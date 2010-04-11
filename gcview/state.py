def set_imperial(args):
    args['SD']['inches'] = True

def set_metric(args):
    args['SD']['inches'] = False

def set_absolute(args):
    args['SD']['absolute'] = True

def set_incremental(args):
    args['SD']['absolute'] = False
