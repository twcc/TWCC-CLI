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

def table_layout(title, json_obj, caption_row=[], debug=False, isWrap=True):
    from terminaltables import AsciiTable, SingleTable
    from colorclass import Color
    from termcolor import cprint
    from textwrap import wrap
    import time

    if type(json_obj) == type({}):
        json_obj = [json_obj]
    if type(json_obj) == type([]):
        if len(json_obj)>0:
            row = json_obj[0]
            caption_row = row.keys()
    heading_cap = set(['id', 'name'])

    intersect = set(caption_row).intersection(heading_cap)

    if len(intersect)>0:
        new_caption = []
        for ele in sorted(intersect):
            new_caption.append( ele )
            caption_row.remove( ele )
        new_caption.extend(sorted(caption_row))
        caption_row = new_caption

    start_time = time.time()

    table_info = []
    table_info.append([ Color("{autoyellow}%s{/autoyellow}"%x) for x in caption_row])

    for ele in json_obj:
        table_info.append([ ele[cap] for cap in caption_row])
    table = AsciiTable(table_info, title)


    for idx in range(len(table.table_data[1])):
        ele = table.table_data[1][idx]
        if type(ele) == type([]) and len(ele)>0: # for list
            tmp = ""
            ptn = "[{0:01d}] {1}\n"
            if len(ele)>9:
                ptn = "[{0:02d}] {1}\n"
            for idy in range(len(ele)):
                tmp += ptn.format(idy+1, ele[idy])
            table.table_data[1][idx] = tmp
        elif type(ele) == type({}): # for dictionary
            tmp = "%s"%"\n".join([ "[%s] %s"%(x, ele[x]) for x in ele.keys()])
            table.table_data[1][idx] = tmp
        elif type(ele) == type(""): # for string
            table.table_data[1][idx] = '\n'.join(wrap(ele, 20))

    print(table.table)
    if debug:
        cprint("- %.3f seconds" % (time.time() - start_time), 'red', attrs=['bold'])

def table_layout_william(title, json_obj, caption_row=None, debug=False):
    from terminaltables import AsciiTable, SingleTable
    from colorclass import Color
    from termcolor import cprint
    import time

    pass
