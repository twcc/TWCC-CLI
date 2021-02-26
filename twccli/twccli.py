# -*- coding: utf-8 -*-
import click
import os
import sys

plugin_folder = os.path.join(os.path.dirname(__file__), 'commands')
os.environ['LANG'] = 'C.UTF-8'
os.environ['LC_ALL'] = 'C.UTF-8'

if "TWCC_DATA_PATH" in os.environ and os.path.isdir(os.environ['TWCC_DATA_PATH']):
    log_dir = "{}/log".format(os.environ['TWCC_DATA_PATH'])
else:
    log_dir = "{}/log".format(os.path.join(os.environ['HOME'], '.twcc_data'))
try:
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
except:
    log_dir = os.environ['HOME']
if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
    from loguru import logger
    logger.remove()
    logger.add(os.path.join(log_dir, "twcc.log"), format="{time:YYYY-MM-DD HH:mm:ss} |【{level}】| {file} {function} {line} | {message}",
               rotation="00:00", retention='20 days', encoding='utf8', level="INFO", mode='a')
else:
    import yaml
    import logging
    import coloredlogs
    import logging.config
    with open('twccli/logging.yml', 'r') as f:
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
        click.echo("[TWCCLI] "+msg, file=sys.stderr)

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


cli = TWCCLI(help='Welcome to TWCC, TaiWan Computing Cloud. '
             'Thanks for using TWCC-CLI https://github.com/TW-NCHC/TWCC-CLI. '
             '-- You Succeed, We Succeed!! --')

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS, cls=TWCCLI)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click.option("-sv", "--show_and_verbose", is_flag=True, help="Enables verbose mode and show in console.")
@pass_environment
def cli(env, verbose, show_and_verbose):
    """
        Welcome to TWCC, TaiWan Computing Cloud.

        https://github.com/TW-NCHC/TWCC-CLI

        version: v0.5.x

        -- You Succeed, We Succeed!! --
    """
    env.verbose = verbose
    check_if_py2()
    if show_and_verbose:
        env.verbose = True
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
    if sys.version_info[0] < 3:
        from os import environ
        __show_deprecated__ = False
        if environ.get('TWCC_SHOW_DEPRECATED') is not None:
            __show_deprecated__ = False if environ.get('TWCC_SHOW_DEPRECATED') == 'False' else True
        if __show_deprecated__:
            print(bcolors.WARNING + "******** Warning from TWCC.ai ********\n" +
                "TWCC-CLI will not support Python 2.7 after 1st Jul., 21'.\nTWCC-CLI 工具即將在中華民國一百一十年七月一日後不再支援 Python 2.7 版。\nPlease update your Python version, or visit https://www.python.org for details.\n請更新您的 Python 工具或請到 https://www.python.org 暸解更多消息。\n" + bcolors.ENDC)


if __name__ == '__main__':
    cli()
