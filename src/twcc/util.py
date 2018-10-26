def parsePtn (url):
    import re
    g = re.findall(r'\{[A-Z]+\}', url)
    return dict([ (x[1:-1], x) for x in g])
