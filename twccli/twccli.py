# -*- coding: utf-8 -*-
import click
import os
import sys
plugin_folder = os.path.join(os.path.dirname(__file__), 'commands')
os.environ['LANG'] = 'C.UTF-8'
os.environ['LC_ALL'] = 'C.UTF-8'

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
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['cli']


cli = TWCCLI(help='Welcome to TWCC, TaiWan Computing Cloud. '
             'Thanks for using TWCC-CLI https://github.com/TW-NCHC/TWCC-CLI. '
             '-- You Succeed, We Succeed!! --')


@click.command(cls=TWCCLI)
@pass_environment
def cli(ctx, ):
    """
        Welcome to TWCC, TaiWan Compute Cloud.

        https://github.com/TW-NCHC/TWCC-CLI

        -- You Succeed, We Succeed!! --
    """
    pass


if __name__ == '__main__':
    cli()
