import threading
import sys, os
import time
import unicodedata

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

def strShorten(mstr, max_len=6):
    if len(mstr)>max_len:
        return u"{}...".format(mstr[:max_len])
    else:
        return mstr

def isNone(x):
    return True if type(x) == type(None) else False

def table_layout(title, json_obj, caption_row=[], debug=False, isWrap=True):
    from terminaltables import AsciiTable, SingleTable
    from colorclass import Color
    from termcolor import cprint
    from textwrap import wrap
    import time
    import json

    if type(json_obj) == type({}):
        json_obj = [json_obj]
    if not len(caption_row)>0 and type(json_obj) == type([]):
        if len(json_obj)>0:
            row = json_obj[0]
            caption_row = list(row.keys())
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
        table_info.append([ ele[cap] for cap in caption_row if cap in ele])
    table = AsciiTable(table_info, title)

    for idy in range(len(table.table_data)):
        for idx in range(len(table.table_data[idy])):
            ele = table.table_data[idy][idx]
            if type(ele) == type([]) and len(ele)>0: # for list
                tmp = ""
                ptn = "[{0:01d}] {1}\n"
                if len(ele)>9:
                    ptn = "[{0:02d}] {1}\n"
                for idz in range(len(ele)):
                    out_buf = ele[idz]
                    try:
                        out_buf = json.loads(out_buf)
                        out_buf = json.dumps(out_buf, indent=2, separators=(',', ': '))
                    except:
                        pass
                    tmp += ptn.format(idy+1, out_buf)
                table.table_data[idy][idx] = tmp
            elif type(ele) == type({}): # for dictionary
                tmp = "%s"%"\n".join([ "[%s] %s"%(x, ele[x]) for x in ele.keys()])
                table.table_data[idy][idx] = tmp
            elif type(ele) == type(""): # for string
                table.table_data[idy][idx] = '\n'.join(wrap(ele, 20))

    print(table.table)
    if debug:
        cprint("- %.3f seconds" % (time.time() - start_time), 'red', attrs=['bold'])

def dic_seperator(d):
    non_dic_cap_table = []
    dic_cap_table = []

    if type(d) is list:
        for key in d[0].keys():
            if type(d[0][key]) is dict:
                dic_cap_table.append(key)
            else:
                non_dic_cap_table.append(key)
    elif type(d) is dict:
        for key in d.keys():
            if type(d[key]) is dict:
                dic_cap_table.append(key)
            else:
                non_dic_cap_table.append(key)

    return non_dic_cap_table,dic_cap_table


def create_table_list(obj,tt):
    from colorclass import Color
    from termcolor import cprint
    from terminaltables import AsciiTable as AC

    import time
    temp_list = []

    temp_list.append([cap for cap in tt])

    for i in range(len(obj)):
        tf = []
        for na in tt:
            if na in ["created_at","expired_time"]:
                ti = time.localtime(int(str(obj[i][na])[:11]))
                tf.append("{}/{}/{}\n{}:{}:{}".format(ti.tm_year,ti.tm_mon,ti.tm_mday,ti.tm_hour,ti.tm_min,ti.tm_sec))
            else:
                tf.append(obj[i][na])
        temp_list.append(tf)

    temp_table = AC(temp_list)

    return temp_table


class SpinCursor(threading.Thread):
    """ A console spin cursor class """

    def __init__(self, msg='',maxspin=0,minspin=10,speed=5):
        # Count of a spin
        self.count = 0
        self.out = sys.stdout
        self.flag = False
        self.max = maxspin
        self.min = minspin
        # Any message to print first ?
        self.msg = msg
        # Complete printed string
        self.string = ''
        # Speed is given as number of spins a second
        # Use it to calculate spin wait time
        self.waittime = 1.0/float(speed*4)
        if os.name == 'posix':
            self.spinchars = (unicodedata.lookup('FIGURE DASH'),u'\\ ',u'| ',u'/ ')
        else:
            # The unicode dash character does not show
            # up properly in Windows console.
            self.spinchars = (u'-',u'\\ ',u'| ',u'/ ')
        threading.Thread.__init__(self, None, None, "Spin Thread")

    def spin(self):
        """ Perform a single spin """

        for x in self.spinchars:
            self.string = self.msg + "...\t" + x + "\r"
            self.out.write(self.string.encode('utf-8'))
            self.out.flush()
            time.sleep(self.waittime)

    def run(self):

        while (not self.flag) and ((self.count<self.min) or (self.count<self.max)):
            self.spin()
            self.count += 1

        # Clean up display...
        self.out.write(" "*(len(self.string) + 1))

    def stop(self):
        self.flag = True
