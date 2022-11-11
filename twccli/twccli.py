# -*- coding: utf-8 -*-
import click
import os
import sys
import yaml
import requests
import feedparser
from os import path
from urllib.parse import urlparse


if "TWCC_DATA_PATH" in os.environ and os.path.isdir(os.environ['TWCC_DATA_PATH']):
    _TWCC_DATA_DIR_ = os.environ['TWCC_DATA_PATH']
else:
    homepath = os.environ['HOME'] if 'HOME' in os.environ else os.environ['HOMEPATH']
    _TWCC_DATA_DIR_ = os.path.join(homepath, '.twcc_data')


def create_log_dir():
    log_dir = os.path.join(_TWCC_DATA_DIR_, "log")

    if not os.path.isdir(log_dir):
        os.mkdir(_TWCC_DATA_DIR_)
        os.mkdir(log_dir)

    return log_dir


plugin_folder = os.path.join(os.path.dirname(__file__), 'commands')
os.environ['LANG'] = 'C.UTF-8'
os.environ['LC_ALL'] = 'C.UTF-8'

log_dir = create_log_dir()


if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
    from loguru import logger
    logger.remove()
    logger.add(os.path.join(log_dir, "twcc.log"), format="{time:YYYY-MM-DD HH:mm:ss} |【{level}】| {file} {function} {line} | {message}",
               rotation="00:00", retention='20 days', encoding='utf8', level="INFO", mode='a')
else:
    import logging
    import coloredlogs
    import logging.config
    PackageYaml = "{}/twccli/yaml/logging.yaml".format(
        os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))))
    with open(PackageYaml, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    log_file_name = config['handlers']['file']['filename']
    config['handlers']['file']['filename'] = os.path.join(
        log_dir, log_file_name)
    logging.config.dictConfig(config)
    logger = logging.getLogger('command')
    coloredlogs.install(level=config['loggers']['command']['level'],
                        fmt=config['formatters']['default']['format'], logger=logger)
    # coloredlogs.install(logger=logger)


class Environment(object):
    def __init__(self):
        self.verbose = False

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo("[TWCCLI] "+msg, file=sys.stdout)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)

    def vlogger_info(self, msg):
        if self.verbose:
            return logger.info(msg)

    def get_verbose(self):
        return self.verbose


pass_environment = click.make_pass_decorator(Environment, ensure=True)


class TWCCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')

        import six
        if six.PY2 == True:
            # FileNotFoundError is only available since Python 3.3
            # https://stackoverflow.com/a/21368457
            FileNotFoundError = IOError
        from io import open

        try:
            with open(fn, 'rb') as f:
                txt = f.read()
        except FileNotFoundError:
            print('Oops.')

        code = compile(txt, fn, 'exec')
        eval(code, ns, ns)
        ns['cli'].name = name
        return ns['cli']


def exception(logger):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur

    @param logger: The logging object
    """

    def decorator(func):

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                # log the exception
                err = "There was an exception in  "
                err += func.__name__
                logger.exception(err)

            # re-raise the exception
            raise
        return wrapper
    return decorator


cli = TWCCLI(help="""
        Welcome to TWCC, TaiWan Computing Cloud.

        https://github.com/twcc/TWCC-CLI

        -- You Succeed, We Succeed!! --

                Powered by TWS
    """)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, cls=TWCCLI)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click.option("-sv", "--show_and_verbose", is_flag=True, help="Enables verbose mode and show in console.")
@pass_environment
def cli(env, verbose, show_and_verbose):
    """
        Welcome to TWCC, TaiWan Computing Cloud.

        https://github.com/twcc/TWCC-CLI

        -- You Succeed, We Succeed!! --

                Powered by TWS
    """
    env.verbose = verbose
    check_if_py2()
    convert_credential()
    if show_and_verbose:
        env.verbose = True
        if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
            logger.add(sys.stderr, level="DEBUG")
    pass


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


def check_if_py2():
    """ obsolete function
    """
    if sys.version_info[0] < 3:
        from os import environ
        __show_deprecated__ = False
        if environ.get('TWCC_SHOW_DEPRECATED') is not None:
            __show_deprecated__ = False if environ.get(
                'TWCC_SHOW_DEPRECATED') == 'False' else True
        if __show_deprecated__:
            print(bcolors.WARNING + "******** Warning from TWCC.ai ********\n" +
                  "TWCC-CLI will not support Python 2.7 after 1st Jul., 21'.\nTWCC-CLI 工具即將在中華民國一百一十年七月一日後不再支援 Python 2.7 版。\nPlease update your Python version, or visit https://www.python.org for details.\n請更新您的 Python 工具或請到 https://www.python.org 暸解更多消息。\n" + bcolors.ENDC)


def convert_credential():
    hdler = CredentialHandler()

    if hdler.isOldCredential():
        click.echo(click.style("Old Credential found! Current credential is version: v%s." % (
            hdler.old_version), bg='blue', fg='white', blink=True, bold=True))

        if click.confirm("Do you want to renew your credentials format?", default=True):
            hdler.renew()


class CredentialHandler():
    def __init__(self):
        self.old_credential = path.join(_TWCC_DATA_DIR_, "credential")

        self._current_version = self.get_current_version()
        create_log_dir()
        from datetime import datetime
        self.backup_credential = path.join(
            _TWCC_DATA_DIR_, "credential.bakup_"+datetime.now().strftime("%m%d%H%M"))

        from .version import __version__
        self.cli_version = __version__

    def get_current_version(self):
        rss_file = "https://pypi.org/rss/project/twcc-cli/releases.xml"
        return feedparser.parse(fetch_and_cache(rss_file))['entries'][0]['title']

    def isOldCredential(self):
        if path.exists(self.old_credential):
            with open(self.old_credential, 'r') as stream:
                try:
                    yaml_cnt = stream.read()
                    if len(yaml_cnt) == 0:
                        return False

                    cnf = yaml.safe_load(yaml_cnt)

                    self.old_api = cnf['_default']['twcc_api_key']
                    self.prj_code = cnf['_default']['twcc_proj_code']
                    self.old_version = cnf['_meta']['cli_version']

                    _env_ver_ = self.old_version.replace("RC", "").split('.')
                    _cli_ver_ = self.cli_version.replace("RC", "").split('.')
                    _online_ver_ = self._current_version.split('.')

                    env_ver_count = int(
                        _env_ver_[0])*10000 + int(_env_ver_[1])*100 + int(_env_ver_[2])*1
                    cli_ver_count = int(
                        _cli_ver_[0])*10000 + int(_cli_ver_[1])*100 + int(_cli_ver_[2])*1
                    online_ver_count = int(
                        _online_ver_[0])*10000 + int(_online_ver_[1])*100 + int(_online_ver_[2])*1

                    if online_ver_count > env_ver_count:
                        mystr = """
 ___________________
 | _______________ |
 | |XXXXXXXXXXXXX| |
 | |XXXXXXXXXXXXX| |
 | |XXXXXXXXXXXXX| |
 |_________________|
 ___[___________]___
|         [_____] []|  \__
L___________________J     \ \___\/

New TWCC-CLI version: {} found in https://pypi.org/project/TWCC-CLI/
Please use `pip3 install -U TWCC-CLI` to upgrade your toolkit.

 _______      _____    ___
|_   _\ \    / / __|  / __|___
  | |  \ \/\/ /\__ \ | (__/ _ \_
  |_|   \_/\_/ |___/  \___\___(_)
   We build and operate TWCC.ai
                        """
                        click.echo_via_pager(
                            mystr.format(self._current_version))
                        # if True, will make user renew credentials (no good)
                        return False
                    if cli_ver_count > env_ver_count:
                        return True
                    return False
                except yaml.YAMLError as exc:
                    print(exc)

    def renew(self):
        """When seeing old version, we need to create a new credential file.
        """

        self._backup()
        self._removeOld()

        from click.testing import CliRunner
        runner = CliRunner()
        cmd_list = "config init --apikey %s -pcode %s -ga" % (
            self.old_api, self.prj_code)
        result = runner.invoke(cli, cmd_list.split(" "))
        stmt = "[Succeful] Successfully convert credential to latest version, %s. " % (
            self.cli_version)
        click.echo(click.style(stmt, fg='green', blink=True))

    def _backup(self):
        from shutil import copyfile
        copyfile(self.old_credential, self.backup_credential)

    def _removeOld(self):
        import os
        os.remove(self.old_credential)

def _fetch_file(url, save_to):
    open(save_to, 'wb').write(requests.get(
        url, allow_redirects=True).content)

def fetch_and_cache(url) -> str:
    filename = urlparse(url).path.split('/')[-1]
    full_path = _TWCC_DATA_DIR_ + path.sep + filename

    if not path.exists(full_path):
        _fetch_file(url, full_path)
    mtime = path.getmtime(full_path)
        
    from datetime import timedelta, datetime
    ts = datetime.fromtimestamp(mtime)
    ts_max = ts + timedelta(days=1)
    if ts > ts_max:
        _fetch_file(url, full_path)
    return open(full_path, 'rb').read()

def _fetch_file(url, save_to):
    open(save_to, 'wb').write(requests.get(
        url, allow_redirects=True).content)


def fetch_and_cache(url) -> str:
    filename = urlparse(url).path.split('/')[-1]
    full_path = _TWCC_DATA_DIR_ + path.sep + filename

    if not path.exists(full_path):
        _fetch_file(url, full_path)
    mtime = path.getmtime(full_path)

    from datetime import timedelta, datetime
    ts = datetime.fromtimestamp(mtime)
    ts_max = ts + timedelta(days=1)
    if ts > ts_max:
        _fetch_file(url, full_path)
    return open(full_path, 'rb').read()


if __name__ == '__main__':
    cli()
