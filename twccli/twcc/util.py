import datetime
import json
import os
import re
import socket
import sys
import threading
import time
import unicodedata
import uuid
from textwrap import wrap
import click
import jmespath
import pytz
import requests as rq
from colorclass import Color
from termcolor import cprint
from terminaltables import AsciiTable
from twccli.twccli import pass_environment

os.environ['LANG'] = 'C.UTF-8'
os.environ['LC_ALL'] = 'C.UTF-8'


def parsePtn(url):
    import re
    g = re.findall(r'\{[A-Z]+\}', url)
    return dict([(x[1:-1], x) for x in g])


def pp(**kwargs):
    import pprint
    mpp = pprint.PrettyPrinter(indent=2)
    mpp.pprint(kwargs)


def jpp(inobj):
    import json
    print(
        json.dumps(inobj,
                   ensure_ascii=False,
                   sort_keys=True,
                   indent=4,
                   separators=(',', ': ')))


@pass_environment
def isDebug(env):
    return True if os.environ.get(
        "TWCC_CLI_STAGE") == "dev" or env.verbose else False


def strShorten(mstr, max_len=6):
    if len(mstr) > max_len:
        return u"{}...".format(mstr[:max_len])
    else:
        return mstr


def isNone(x):
    return True if type(x) == type(None) else False


def check_empty_value(x) -> bool:
    """make sure input value is empty

    Args:
        x (str): any parameter

    Returns:
        True: if input parameter is empty or None, else is False
    """
    return True if isNone(x) or len(x) == 0 else False


def mkdir_p(path):
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def isFile(fn):
    return True if os.path.isfile(fn) else False


def resource_id_validater(mid):
    return mid.isdigit()


def _table_layout_set_default_caption(json_obj, caption_row, keep_order=False):
    heading_cap = set(['id', 'name'])
    if not len(caption_row) > 0 and type(json_obj) == type([]):
        if len(json_obj) > 0:
            row = json_obj[0]
            caption_row = list(row.keys())

    if keep_order == True:
        pass
    else:
        intersect = set(caption_row).intersection(heading_cap)
        if len(intersect) > 0:
            new_caption = []
            for ele in sorted(intersect):
                new_caption.append(ele)
                caption_row.remove(ele)
            new_caption.extend(sorted(caption_row))
            caption_row = new_caption

    return caption_row


def _table_layout_data_cell_format(cell_ele, is_warp=True):
    ele = cell_ele
    if type(ele) == type([]) and len(ele) > 0:  # for list
        tmp = ""
        ptn = "[{0:02d}] {1}\n" if len(ele) > 9 else "[{0:01d}] {1}\n"
        for idz in range(len(ele)):
            out_buf = ele[idz]
            try:
                out_buf = json.loads(out_buf)
                out_buf = json.dumps(out_buf, indent=2, separators=(',', ': '))
            except:
                pass
            tmp += ptn.format(idz+1, out_buf)
        return tmp
    elif type(ele) == type({}):  # for dictionary
        tmp = "%s" % "\n".join(["[%s] %s" % (x, ele[x]) for x in ele.keys()])
        return tmp
    elif type(ele) == type(""):  # for string
        return '\n'.join(wrap(ele, 20)) if is_warp else ele


def _table_layout_colorful_val(val):
    if type(val)==type([]):
        return val

    val = '' if val == None else val
    return Color("{autored}%s{/autored}" %
                 val) if ("%s" % val).lower() == "error" else "%s" % val


def _table_layout_arrange_table_info(json_obj, caption_row):
    table_info = []
    table_info.append([x for x in caption_row])
    for ele in json_obj:
        row_data = []
        for cap in caption_row:
            try:
                val = jmespath.search(cap, ele)
            except jmespath.exceptions.ParseError:
                val = ele[cap] if cap in ele else ''

            row_data.append(_table_layout_colorful_val(val))
        table_info.append(row_data)
    return table_info


def _table_layout_data_cell_layout(list_of_list, is_warp=True):
    for idy in range(len(list_of_list)):
        for idx in range(len(list_of_list[idy])):
            list_of_list[idy][idx] = _table_layout_data_cell_format(
                list_of_list[idy][idx], is_warp)
    return list_of_list


def table_layout(title,
                 json_obj,
                 caption_row=[],
                 debug=False,
                 is_warp=True,
                 max_len=10,
                 isPrint=False,
                 captionInOrder=False):
    json_obj = [json_obj] if type(json_obj) == type({}) else json_obj
    caption_row = _table_layout_set_default_caption(json_obj,
                                                    caption_row,
                                                    keep_order=captionInOrder)

    start_time = time.time()

    table = AsciiTable(_table_layout_arrange_table_info(json_obj, caption_row),
                       title=" {} ".format(title))

    table.table_data = _table_layout_data_cell_layout(table.table_data,
                                                      is_warp=is_warp)

    if debug:
        cprint("- %.3f seconds" % (time.time() - start_time),
               'red',
               attrs=['bold'])

    if isPrint:
        print(table.table)
    else:
        return table.table


def send_ga(event_name, cid, params):

    if isNone(cid) or len(cid) == 0:
        return True

    measurement_id = 'G-6S0562GHKE'
    api_secret = 'wNf5Se9QSP2YdvgIjfAHiw'
    host = 'https://www.google-analytics.com'
    uri = '/mp/collect?measurement_id={}&api_secret={}'.format(
        measurement_id, api_secret)
    payload = {
        "client_id": cid,
        "non_personalized_ads": "false",
        "events": [{
            "name": event_name[:39],
            "params": params
        }]
    }
    headers = {'content-type': 'application/json'}

    if isDebug():
        from ..twccli import logger
        logger_info = {
            'payload': payload,
            'headers': headers,
            'endpoint': host + uri
        }
        logger.info(logger_info)

    res = rq.post(host + uri, data=json.dumps(payload), headers=headers)


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

    return non_dic_cap_table, dic_cap_table


def timezone2local(time_str):
    if '.' in time_str:
        time_str = time_str[:-8] + 'Z'
    if 'T' in time_str and 'Z' in time_str:
        ans = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
    elif 'T' in time_str:
        ans = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
    return pytz.utc.localize(ans, is_dst=None).astimezone(
        pytz.timezone('Asia/Taipei'))


def create_table_list(obj, tt):
    import time

    from terminaltables import AsciiTable as AC
    temp_list = []

    temp_list.append([cap for cap in tt])

    for i in range(len(obj)):
        tf = []
        for na in tt:
            if na in ["created_at", "expired_time"]:
                ti = time.localtime(int(str(obj[i][na])[:11]))
                tf.append("{}/{}/{}\n{}:{}:{}".format(ti.tm_year, ti.tm_mon,
                                                      ti.tm_mday, ti.tm_hour,
                                                      ti.tm_min, ti.tm_sec))
            else:
                tf.append(obj[i][na])
        temp_list.append(tf)

    temp_table = AC(temp_list)

    return temp_table


class SpinCursor(threading.Thread):
    """ A console spin cursor class """

    def __init__(self, msg='', maxspin=0, minspin=10, speed=5):
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
        self.waittime = 1.0 / float(speed * 4)
        if os.name == 'posix':
            self.spinchars = (unicodedata.lookup('FIGURE DASH'), u'\\ ', u'| ',
                              u'/ ')
        else:
            # The unicode dash character does not show
            # up properly in Windows console.
            self.spinchars = (u'-', u'\\ ', u'| ', u'/ ')
        threading.Thread.__init__(self, None, None, "Spin Thread")

    def spin(self):
        """ Perform a single spin """

        for x in self.spinchars:
            self.string = self.msg + "...\t" + x + "\r"
            self.out.write(self.string.encode('utf-8'))
            self.out.flush()
            time.sleep(self.waittime)

    def run(self):

        while (not self.flag) and ((self.count < self.min) or
                                   (self.count < self.max)):
            self.spin()
            self.count += 1

        # Clean up display...
        self.out.write(" " * (len(self.string) + 1))

    def stop(self):
        self.flag = True


def mk_names(name, ids_or_names):
    if not isNone(name):
        ids_or_names += (name, )
    return tuple(set(ids_or_names))


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def validate(apikey):
    try:
        return re.match(
            '^([0-9a-fA-F]{8})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{12})$',
            apikey)
    except:
        return False


def name_validator(name):
    """
    rules are in twcc/twcc-cli#98

        :param name: validating name
        :type name: string
        :return: validate or not
        :rtype: bool
    """
    if re.match("^[a-z][a-z-_0-9]{5,15}$", name):
        return True
    return False


def mkCcsHostName(ip_addr):
    return "%s.ccs.twcc.ai" % ("-".join(ip_addr.split(".")))


def window_password_validater(password):
    import re
    if len(password) >= 17 and len(password) <= 72:
        result = True
        if not re.search("[A-Z]", password):
            click.echo("For Windows upper case latter is needed, [A-Z].")
            result = False
        if result and not re.search("[a-z]", password):
            click.echo("For Windows upper case latter is needed,[a-z].")
            result = False
        if result and not re.search("[0-9]", password):
            click.echo("For Windows numeric latter is needed, [0-9].")
            result = False
        if result and not re.search("[@$!%*?&]", password):
            click.echo("For Windows special character is needed, [@$!%*?&].")
            result = False
        return result
    else:
        click.echo("Your password is too long or too short, length: %s" %
                   (len(password)))
        return False


def get_environment_params(param_key, def_val=None):
    if param_key in os.environ and len(os.environ[param_key]) > 0:
        def_val = os.environ[param_key]
    return def_val


def twcc_error_echo(msg):
    """twcc standard error echo

    Args:
        msg (string): error message
    """
    import click

    click.echo(click.style('[TWCC-CLI] Error-', fg='bright_red'), nl=False)
    click.echo(msg)


def protection_desc(x):
    return "    Y" if x['termination_protection'] else " "


def _debug(mesg, is_pause=True):
    click.echo(click.style("\t[DEBUG]: %s" % (mesg), bg='red', fg='white'))

    if is_pause:
        click.pause()


def get_flavor_string(gpu, cpu, mem):
    if gpu > 0:
        return "{} GPU, {} vCores, {:d} Gib Memory".format(
            gpu, cpu, int(mem / 1024))
    return "{} vCores, {:d} Gib Memory".format(cpu, int(mem / 1024))


def is_vcs_env():
    import socket
    host_name = socket.gethostname()
    if re.search('-iaas$', host_name):
        return True
    return False


def set_rc_config(rc):
    lang_encoding = """
    export PYTHONIOENCODING=UTF-8
    """

    lang_encoding_centos79 = """
    export LANG=zh_TW.utf-8
    export LC_ALL=zh_TW.utf-8
    export PYTHONIOENCODING=UTF-8
    """
    if not rc:
        return False

    try:
        import platform
        core_version = platform.linux_distribution()
    except:
        import distro
        core_version = distro.linux_distribution()

    if core_version[0] == 'CentOS Linux' and core_version[1][:3] == '7.9':
        lang_encoding = lang_encoding_centos79

    if rc:
        click.echo("Add language setting to `.bashrc`.")
        open(os.environ["HOME"]+"/.bashrc", 'a').write(lang_encoding)
    else:
        click.echo(
            "Please add encoding setting to your environment: \n {}".format(lang_encoding))
    try:
        open(os.environ["HOME"]+"/.bashrc", 'a').write(". {}/twccli/twccli-complete.sh".format(
            [cli_path for cli_path in sys.path if '.local/lib' in cli_path][0]))
    except Exception:
        pass

    return True

def set_cid_flag(ga_flag=True):
    if not ga_flag == None:
        return str(uuid.uuid1()) if ga_flag else None
    else:
        ga_agree_flag = click.confirm(
            'Do you agree we use the collection of the information by GA to improve user experience? ', default=True)
        return str(uuid.uuid1()) if ga_agree_flag else None
