#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: site_facts_network

short_description: Identify internal and external interfaces on ScotGrid Glasgow hosts

version_added: "2.4"

description:
    - "Identify internal and external interfaces on ScotGrid Glasgow hosts"

author:
    - Gordon Stewart
'''

EXAMPLES = '''
# Identify internal and external network interfaces
- name: Identify internal and external network interfaces
  site_facts_network:
'''

RETURN = '''
'''

import subprocess

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # Seed the result dict
    result = dict(
        changed = False,
    )

    # Instantiate AnsibleModule object
    module = AnsibleModule(
        argument_spec = {},
        supports_check_mode = True
    )

    # Obtain network configuration via 'ip' command
    p = subprocess.Popen(['/usr/sbin/ip', '-oneline', 'addr', 'show'], stdout = subprocess.PIPE)
    (out, err) = p.communicate()

    if_internal = None
    if_external = None

    # Iterate over interfaces
    for l in out.splitlines():
        l = l.split()

        # Ignore IPv6 configuration (TODO: revisit as necessary)
        if l[2] == 'inet6':
            continue

        # Check IPv4 address (n.b. this is not portable, and assumes at most one internal and one external interface per host)
        name = l[1]
        ipv4 = l[3]
        if ipv4.startswith('10.1.'):
            if_internal = name
        elif ipv4.startswith('130.209.239.'):
            if_external = name

    result['ansible_facts'] = {}
    result['ansible_facts']['if_internal'] = if_internal
    result['ansible_facts']['if_external'] = if_external
    result['message'] = 'Internal: {0}  External: {1}'.format(if_internal, if_external)

    # Return results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
