def parsePtn(url):
    import re
    g = re.findall(r'\{[A-Z]+\}', url)
    return dict([(x[1:-1], x) for x in g])


def pp(**kwargs):
    import pprint
    mpp = pprint.PrettyPrinter(indent=2)
    mpp.pprint(kwargs)


def jpp(**args):
    import json
    print (json.dumps({'4': 5, '6': 7}, sort_keys=True, indent=2))


def isNone(x):
    return True if type(x) == type(None) else False
