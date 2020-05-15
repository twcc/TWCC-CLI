#!/usr/bin/env python

'''
TWCC custom dynamic inventory script for Ansible.

credit: https://www.jeffgeerling.com/blog/creating-custom-dynamic-inventories-ansible
'''

import os
import sys
import argparse
import json
from twccli.twcc.services.compute_util import list_vcs
from twccli.twcc.util import jpp

try:
    import json
except ImportError:
    import simplejson as json

class TwccInventory(object):

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.twcc_inventory()
            #self.inventory = self.example_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()

        jpp(self.inventory)

    def twcc_inventory(self):
        vcs = list_vcs([], False, is_print=False)
        res = { "group":{'hosts':[],
                         'vars':{
                            'ansible_ssh_user': 'ubuntu',
                            'ansible_python_interpreter': '/usr/bin/python3.5',
                            }},
                "_meta":{'hostvars':{}} }

        res['group']['hosts']=[ srv['public_ip'] for srv in vcs if not len(srv['public_ip'])==0]
        return res

    # Example inventory for testing.
    def example_inventory(self):
        return {
            'group': {
                'hosts': ['192.168.28.71', '192.168.28.72'],
                'vars': {
                    'ansible_ssh_user': 'vagrant',
                    'ansible_ssh_private_key_file':
                        '~/.vagrant.d/insecure_private_key',
                    'example_variable': 'value'
                }
            },
            '_meta': {
                'hostvars': {
                    '192.168.28.71': {
                        'host_specific_var': 'foo'
                    },
                    '192.168.28.72': {
                        'host_specific_var': 'bar'
                    }
                }
            }
        }

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

# Get the inventory.
TwccInventory()
