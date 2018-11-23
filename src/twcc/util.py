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
    print(json_obj) 
    print(type(json_obj))
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
        final_cap = table_cap
        temp = []
        for data_d in table_cap:
            if type(json_obj[data_d]) is dict:
                table_layout(data_d,json_obj[data_d])
                final_cap.remove(data_d)
            elif type(json_obj[data_d]) is not str:
                print(json_obj[data_d])
                print(data_d)
                temp.append(str(json_obj[data_d])[:20])
            pass
        table_info.append(temp)   
        table_info.insert(0,[ Color("{autoyellow}%s{/autoyellow}"%x) for x in final_cap])

    table = AsciiTable(table_info,title)
    print(table.table)



