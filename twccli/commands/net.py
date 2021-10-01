from twccli.twcc.services.compute import GpuSite, VcsSite, VcsSecurityGroup, VcsServerNet
from twccli.twcc.util import isNone, mk_names
from twccli.twcc.services.compute import getServerId, getSecGroupList
from twccli.twcc.services.compute_util import list_vcs
from twccli.twccli import pass_environment, logger
from twccli.twcc.services.base import Keypairs
from twccli.twcc.services.generic import GenericService
import click
import re
import sys


@click.command(help='Manage CCS (Container Compute Service) ports.')
@click.option('-p',
              '--port',
              'port',
              type=int,
              required=True,
              help='Port number.')
@click.option('-s',
              '--site-id',
              'siteId',
              type=int,
              required=True,
              help='ID of the container.')
@click.option('-open/-close',
              '--open-port/--close-port',
              'isAttach',
              is_flag=True,
              show_default=True,
              help='opens/close container ports.')
@pass_environment
def ccs(env, siteId, port, isAttach):
    """Command line for network function of ccs
    Functions:
    expose/unbind port

    :param port: Port number for your VCS environment
    :type port: integer
    :param siteId: Resource id for VCS
    :type siteId: integer
    :param isAttach: exposed/un-exposed port for continer services
    :type isAttach: bool
    """
    b = GpuSite()
    tsite = b.queryById(siteId)
    if isAttach:
        b.exposedPort(siteId, port)
    else:
        b.unbindPort(siteId, port)


@click.command(help='Manage VCS (Virtual Compute Service) security groups.')
@click.option('-p', '--port', 'port', type=int, help='Port number.')
@click.option('-s',
              '--site-id',
              'siteId',
              type=int,
              required=True,
              help='ID of the container.')
@click.option('-cidr',
              '--cidr-network',
              'cidr',
              type=str,
              help='Network range for security group.',
              default='192.168.0.1/24',
              show_default=True)
@click.option('-fip / -nofip',
              '--floating-ip / --no-floating-ip',
              'fip',
              is_flag=True,
              default=None,
              show_default=False,
              help='Configure your instance with or without a floating IP.')
@click.option('-in/-out',
              '--ingress/--egress',
              'isIngress',
              is_flag=True,
              default=True,
              show_default=True,
              help='Applying security group directions.')
@click.option(
    '-prange',
    '--port-range',
    'portrange',
    type=str,
    help='Port number from min-port to max-port, use "-" as delimiter, ie: 3000-3010.'
)
@click.option('-proto',
              '--protocol',
              'protocol',
              type=str,
              help='Manage VCS security groups protocol.',
              default='tcp',
              show_default=True)
@click.argument('site_ids', nargs=-1)
@pass_environment
def vcs(env, site_ids, siteId, port, cidr, protocol, isIngress, fip, portrange):
    """Command line for network function of vcs
    :param portrange: Port range number for your VCS environment
    :type portrange: string
    :param fip: Configure your VCS environment with or without floating IP
    :type fip: bool
    :param port: Port number for your VCS environment
    :type port: integer
    :param siteId: Resource id for VCS
    :type siteId: integer
    :param cidr: Network range for security group
    :type cidr: string
    :param protocol: Network protocol for security group
    :type protocol: string
    :param isIngress: Applying security group directions.
    :type isIngress: bool
    """
    avbl_proto = ['tcp', 'udp', 'icmp']
    if not protocol in avbl_proto:
        raise ValueError(
            "Protocol is not valid. available: {}.".format(avbl_proto))
    # case 1: floating ip operations
    site_ids = mk_names(siteId, site_ids)
    if len(site_ids) == 0:
        raise ValueError("Error: VCS id: {} is not found.".format(siteId))
        
    site_infos = list_vcs(site_ids, False, is_print=False)

    for site_info in site_infos:
        
        errorFlg = True
        if len(site_info['public_ip']) > 0 and fip == False:
            VcsServerNet().deAssociateIP(site_info['id'])
            errorFlg = False

        if len(site_info['public_ip']) == 0 and fip == True:
            VcsServerNet().associateIP(site_info['id'])
            errorFlg = False

        # case 2: port setting
        from netaddr import IPNetwork
        IPNetwork(cidr)

        secg_list = getSecGroupList(site_info['id'])
        secg_id = secg_list['id']

        if not isNone(portrange):
            if re.findall('[^0-9-]', portrange):
                raise ValueError('port range should be digital-digital')


            port_list = portrange.split('-')
            if len(port_list) == 2:
                port_min, port_max = [int(mport) for mport in port_list]
                if port_min < 0 or port_max < 0:
                    raise ValueError('port range must bigger than 0')
                elif port_min > port_max:
                    raise ValueError(
                        'port_range_min must be <= port_range_max')
            else:
                raise ValueError('port range set error')

            secg = VcsSecurityGroup()
            secg.addSecurityGroup(secg_id, port_min, port_max, cidr, protocol,
                                  "ingress" if isIngress else "egress")
            errorFlg = False

        if not isNone(port):
            secg = VcsSecurityGroup()
            secg.addSecurityGroup(secg_id, port, port, cidr, protocol,
                                  "ingress" if isIngress else "egress")
            errorFlg = False

        if errorFlg:
            raise ValueError(
                "Error! Nothing to do! Check `--help` for detail.")


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, help="NETwork related operations.")
def cli():
    try:
        import sys
        ga = GenericService()
        func_call = '_'.join([i for i in sys.argv[1:] if re.findall(r'\d',i) == [] and not i == '-sv']).replace('-','')
        ga._send_ga(func_call)
    except Exception as e:
        logger.warning(e)
    pass


cli.add_command(ccs)
cli.add_command(vcs)


def main():
    cli()


if __name__ == "__main__":
    main()
