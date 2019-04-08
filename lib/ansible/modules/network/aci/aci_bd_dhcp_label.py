#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: aci_bd_dhcp_label
short_description: Manage DHCP Label on Cisco ACI fabrics (dhcp:Lbl)
description:
- Manage DHCP Label on Cisco ACI fabrics (dhcp:Lbl)
- More information from the internal APIC class
  I(dhcp:Lbl) at U(https://pubhub-prod.s3.amazonaws.com/media/apic-mim-ref/docs/MO-dhcpLbl.html).
author:
- sig9 (sig9@sig9.org)
version_added: '2.7'
requirements:
- ACI Fabric 1.0(3f)+
notes:
- A DHCP relay label contains a name for the label, the scope, and a DHCP option policy.
  The scope is the owner of the relay server and the DHCP option policy supplies DHCP clients
  with configuration parameters such as domain, nameserver, and subnet router addresses.
options:
  bd:
    description:
    - The name of the Bridge Domain.
    required: yes
  description:
    description:
    - Specifies a description of the policy definition.
    required: no
  dhcp_label:
    description:
    - The name of the DHCP Relay Label.
    required: yes
  dhcp_option:
    description:
    - The DHCP option is used to supply DHCP clients with configuration parameters
      such as a domain, name server, subnet, and network address.
    required: no
  owner:
    description:
    - Represents the target relay servers ownership.
    required: yes
    choices: [ infra, tenant ]
    default: infra
  tenant:
    description:
    - The name of the Tenant.
    aliases: [ tenant_name ]
    required: yes
'''

EXAMPLES = r'''
- name: Create a new DHCP Relay Label in a Bridge Domain
  aci_bd_dhcp_label:
    host: "{{ apic }}"
    username: "{{ username }}"
    password: "{{ password }}"
    validate_certs: false
    tenant: "{{ tenant }}"
    bd: "{{ inventory_hostname }}"
    dhcp_label: "{{ dhcp_label }}"
    owner: "{{ owner }}"
    state: "present"

- name: Create a new DHCP Relay Label with an option policy in a Bridge Domain
  aci_bd_dhcp_label:
    host: "{{ apic }}"
    username: "{{ username }}"
    password: "{{ password }}"
    validate_certs: false
    tenant: "{{ tenant }}"
    bd: "{{ inventory_hostname }}"
    dhcp_label: "{{ dhcp_label }}"
    dhcp_option: "{{ dhcp_option }}"
    owner: "{{ owner }}"
    state: "present"

- name: Remove a DHCP Relay Label from a Bridge Domain
  aci_bd_dhcp_label:
    host: "{{ apic }}"
    username: "{{ username }}"
    password: "{{ password }}"
    validate_certs: false
    tenant: "{{ tenant }}"
    bd: "{{ inventory_hostname }}"
    dhcp_label: "{{ dhcp_label }}"
    owner: "{{ owner }}"
    state: "absent"

- name: Query a DHCP Relay Label of a Bridge Domain
  aci_bd_dhcp_label:
    host: "{{ apic }}"
    username: "{{ username }}"
    password: "{{ password }}"
    validate_certs: false
    tenant: "{{ tenant }}"
    bd: "{{ inventory_hostname }}"
    dhcp_label: "{{ dhcp_label }}"
    state: "query"
'''

RETURN = r'''
#
'''

from ansible.module_utils.network.aci.aci import ACIModule, aci_argument_spec
from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = aci_argument_spec()
    argument_spec.update(
        bd=dict(type='str', aliases=['bd_name', 'bridge_domain']),
        dhcp_label=dict(type='str', aliases=['label', 'label_name', 'name']),
        dhcp_option=dict(type='str', aliases=['option', 'option_policy']),
        owner=dict(type='str', default='infra', aliases=['scope'], choices=['infra', 'tenant']),
        state=dict(type='str', default='present', choices=['absent', 'present', 'query']),
        tenant=dict(type='str', aliases=['tenant_name']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'absent', ['dhcp_label', 'bd', 'tenant']],
            ['state', 'present', ['dhcp_label', 'bd', 'tenant']],
        ],
    )

    aci = ACIModule(module)

    bd = module.params['bd']
    label = module.params['dhcp_label']
    option = module.params['dhcp_option']
    owner = module.params['owner']
    state = module.params['state']
    tenant = module.params['tenant']

    aci.construct_url(
        root_class=dict(
            aci_class='fvTenant',
            aci_rn='tn-{0}'.format(tenant),
            target_filter='eq(fvTenant.name, "{0}")'.format(tenant),
            module_object=tenant,
        ),
        subclass_1=dict(
            aci_class='fvBD',
            aci_rn='BD-{0}'.format(bd),
            target_filter='eq(fvBD.name, "{0}")'.format(bd),
            module_object=bd,
        ),
        subclass_2=dict(
            aci_class='dhcpLbl',
            aci_rn='dhcplbl-{0}'.format(label),
            target_filter='eq(dhcpLbl.name, "{0}")'.format(label),
            module_object=label,
        ),
        child_classes=['dhcpRsDhcpOptionPol'],
    )

    aci.get_existing()

    if state == 'present':
        aci.payload(
            aci_class='dhcpLbl',
            class_config=dict(
                name=label,
                owner=owner,
            ),
            child_configs=[
                {'dhcpRsDhcpOptionPol': {'attributes': {'tnDhcpOptionPolName': option}}},
            ]
        )

        aci.get_diff(aci_class='dhcpLbl')

        aci.post_config()

    elif state == 'absent':
        aci.delete_config()

    aci.exit_json()


if __name__ == "__main__":
    main()
