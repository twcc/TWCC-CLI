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
              'site_id',
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
def ccs(env, site_id, port, isAttach):
    """Command line for network function of ccs
    Functions:
    expose/unbind port

    :param port: Port number for your VCS environment
    :type port: integer
    :param site_id: Resource id for VCS
    :type site_id: integer
    :param isAttach: exposed/un-exposed port for continer services
    :type isAttach: bool
    """
    b = GpuSite()
    tsite = b.queryById(site_id)
    if isAttach:
        b.exposedPort(site_id, port)
    else:
        b.unbindPort(site_id, port)

def net_vcs_protocol_check(protocol):
    avbl_proto = ['ah', 'pgm', 'tcp', 'ipv6-encap', 'dccp', 'igmp', 'icmp', 'esp', 'vrrp', 'ipv6-icmp', 'gre', 'sctp', 'rsvp', 'ipv6-route', 'udp', 'ipv6-opts', 'ipv6-nonxt', 'udplite', 'egp', 'ipip', 'icmpv6', 'ipv6-frag', 'ospf']
    if not protocol in avbl_proto:
        pronum = re.findall('^([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])$',protocol)
        if pronum:
            protocol = str(int(pronum[0]))
        else:
            raise ValueError(
                "Protocol is not valid. available: {}.".format(avbl_proto))

def public_ip_assignee(site_info, fip, eip):
    errorFlg = True
    if len(site_info['public_ip']) > 0 and fip == False:
        VcsServerNet().deAssociateIP(site_info['id'])
        errorFlg = False

    if len(site_info['public_ip']) == 0:
        if not isNone(eip):
            VcsServerNet().associateIP(site_info['id'], eip_id = eip)
            errorFlg = False
        elif fip == True:
            VcsServerNet().associateIP(site_info['id'])
            errorFlg = False
    return errorFlg

def max_min_port_check(portrange):
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
    return port_min, port_max

@click.command(help='Manage VCS (Virtual Compute Service) security groups.')
@click.option('-p', '--port', 'port', type=int, help='Port number.')
@click.option('-s',
              '--site-id',
              'site_id',
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
@click.option('-ip',
              '--eip',
              'eip',
              type=str,
              default=None,
              show_default=False,
              help='Configure your instance with a EIP.')
@click.option('-in/-out',
              '--ingress/--egress',
              'is_ingress',
              is_flag=True,
              default=True,
              show_default=True,
              help='Applying security group directions.')
@click.option(
    '-prange',
    '--port-range',
    'portrange',
    type=str,
    help='Port number from min-port to max-port, use "-" as delimiter, ie: 3000-3010. Only supported for TCP, UDP, UDPLITE, SCTP and DCCP'
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
def vcs(env, site_ids, site_id, port, cidr, protocol, is_ingress, fip, portrange, eip):
    """Command line for network function of vcs
    :param portrange: Port range number for your VCS environment
    :type portrange: string
    :param fip: Configure your VCS environment with or without floating IP
    :type fip: bool
    :param port: Port number for your VCS environment
    :type port: integer
    :param site_id: Resource id for VCS
    :type site_id: integer
    :param cidr: Network range for security group
    :type cidr: string
    :param protocol: Network protocol for security group
    :type protocol: string
    :param is_ingress: Applying security group directions.
    :type is_ingress: bool
    """
    net_vcs_protocol_check(protocol)
    # case 1: floating ip operations
    site_ids = mk_names(site_id, site_ids)
    if len(site_ids) == 0:
        raise ValueError("Error: VCS id: {} is not found.".format(site_id))
        
    site_infos = list_vcs(site_ids, False, is_print=False)

    for site_info in site_infos:
        errorFlg = public_ip_assignee(site_info, fip, eip)

        # case 2: port setting
        from netaddr import IPNetwork
        IPNetwork(cidr)

        secg_list = getSecGroupList(site_info['id'])
        secg_id = secg_list['id']

        if not isNone(portrange):
            port_min, port_max = max_min_port_check(portrange)

            secg = VcsSecurityGroup()
            secg.addSecurityGroup(secg_id, port_min, port_max, cidr, protocol,
                                  "ingress" if is_ingress else "egress")
            errorFlg = False

        if not isNone(port):
            secg = VcsSecurityGroup()
            secg.addSecurityGroup(secg_id, port, port, cidr, protocol,
                                  "ingress" if is_ingress else "egress")
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
