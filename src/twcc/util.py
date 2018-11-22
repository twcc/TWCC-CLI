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


def table_layout(title, json_obj, caption_row=None, debug=False):
    from terminaltables import AsciiTable, SingleTable
    from colorclass import Color
    from termcolor import cprint
    import time
    
    table_info = []
    if type(json_obj) is list:
        table_cap = [head for head in json_obj[0].keys()]
        table_info.append([ Color("{autoyellow}%s{/autoyellow}"%x) for x in table_cap])
        for data_d in json_obj:
            temp = []
            for data in data_d:
                temp.append(data_d[data])
            table_info.append(temp)
    elif type(json_obj) is dict:
        table_cap = [head for head in json_obj.keys()]
        print(table_cap)
        table_info.append([ Color("{autoyellow}%s{/autoyellow}"%x) for x in table_cap])
        temp = []
        for data_d in table_cap:
            #temp.append(json_obj[data_d][:20])
            print(json_obj[data_d])
        table_info.append(temp)   

    table = AsciiTable(table_info,title)
    table1 = SingleTable(table_info,title)    
    print(table.table)
    print(table1.table)



