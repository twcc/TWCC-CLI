#!/usr/bin/python

# Copyright: (c) 2020, August Chao <1803001@narlabs.org.tw>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
import re
from twccli.twcc.services.compute_util import list_vcs, create_vcs, del_vcs, doSiteStable
from twccli.twcc.services.compute import VcsServerNet

def_state_map = {"Ready": "started",
                 "Deleted": "deleted"}
def getAnsibleState(twcc_state):
    if twcc_state in def_state_map:
        return def_state_map[twcc_state]
    else:
        return "TBD"

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'TWCC-CLI Team'
}

DOCUMENTATION = '''
---
module: vcs_op

short_description: This is VCS Operstaion module for TWCC

version_added: "0.1"

description:
    - "This module is for operating TWCC VCS instances"

options:
    resource_id:
        description:
            - This is the resource id for your VCS instance.
        required: true
    state:
        description:
            - Control VCS instance to be what state, e.g., started, stopped, restarted, deleted.
        required: false

extends_documentation_fragment:
    - twcc

author:
    - TWCC-CLI Team
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_test:
    resource_id: 981223

# pass in a message and have changed true
- name: Test with a message and changed output
  my_test:
    resource_id: 981223
    state: started
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
    returned: always
message:
    description: The output message that the test module generates
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=False),
        resource_id=dict(type='int', required=False),
        state=dict(type='str', required=False, default=False),
        keypair=dict(type='str', required=False, default=False),
        floating_ip=dict(type='bool', required=False, default=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)


    tvcs = []
    if module.params['name']:
        vcs = list_vcs([], False, is_print=False)
        tvcs = [ x for x in vcs if re.search(module.params['name'], x['name'])]

    if module.params['resource_id']:
        tvcs = list_vcs([module.params['resource_id']], False, is_print=False)

    processed_vcs = []
    if module.params['state']:
        if len(tvcs)>0:
            for x in tvcs:
                if module.params['state'] == getAnsibleState(x['status']):
                    result['changed'] = False
                else:
                    del_vcs([str(x['id'])], isForce=True)
                    result['changed'] = True
                processed_vcs.append(str(x['id']))

        else:
            # if no tvcs, need to create
            if module.params['state'] == 'started':
                tsol = "ubuntu"
                if module.params['keypair']:
                    ans = create_vcs(name = module.params['name'],
                            keypair = module.params['keypair'],
                            sol = "ubuntu", flavor = 'v.xsuper', sys_vol = 'ssd')
                    if 'id' in ans:
                        doSiteStable(ans['id'], site_type='vcs')
                    result['changed'] = True
                    processed_vcs.append(str(ans['id']))


    ## check if floating ip needed
    if module.params['floating_ip']:
        [ VcsServerNet().associateIP(x) for x in processed_vcs ]
    else:
        [ VcsServerNet().deAssociateIP(x) for x in processed_vcs ]


    if len(processed_vcs) > 0:
        result['original_message'] = list_vcs(processed_vcs, False, is_print=False)
    else:
        result['original_message'] = processed_vcs

    result['message'] = 'twccli-vcs'

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
