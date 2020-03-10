# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import os
from twccli.twcc.util import validate, isNone
from twccli.twcc.session import Session2
from twccli.twccli import pass_environment


@click.command(help='Get exsiting info.')
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@pass_environment
def whoami(ctx, verbose):
    ctx.verbose = verbose
    ctx.log("Hi, {}, nice to meet you!".format(
        Session2._whoami()['display_name']))
    print(Session2())


@click.command(help='Initialize CLI environment')
@click.option('--apikey', 'apikey',
              help="TWCC API Key for CLI. It also can read $TWCC_API_KEY.")
@click.option('-pcode', '--project-code', 'proj_code',
              help="TWCC project code for default, ie: GOV108009.")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@pass_environment
def init(ctx, apikey, proj_code, verbose):
    ctx.verbose = verbose
    if not Session2._isValidSession():
        if isNone(apikey):
            if 'TWCC_API_KEY' in os.environ:
                apikey = os.environ['TWCC_API_KEY']
        else:
            os.environ['TWCC_API_KEY'] = apikey

        if not isNone(proj_code):
            if not 'TWCC_PROJ_CODE' in os.environ:
                # raw_input("assign pcode:{}".format(proj_code))
                os.environ['TWCC_PROJ_CODE'] = proj_code
            else:
                raise ValueError(
                    "$TWCC_PROJ_CODE or `--project-code` is required.")
        if validate(apikey):
            ctx.vlog("Receiving Project Code: %s", (proj_code))
            ctx.vlog("Receiving API Key: %s", (apikey))
            Session2(twcc_api_key=apikey)

            click.echo(click.style("Hi! {}, welcome to TWCC!".format(
                Session2._whoami()['display_name']), fg='yellow'))
        else:
            raise ValueError("API Key is not validated.")
    else:
        ctx.log("load credential from {}".format(Session2()._getSessionFile()))
        print(Session2())


@click.group(help="TWCC CLI configuration process.")
def cli():
    pass


cli.add_command(whoami)
cli.add_command(init)


def main():
    cli()


if __name__ == "__main__":
    main()
