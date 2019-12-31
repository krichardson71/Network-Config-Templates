#!/usr/bin/env python
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler
from getpass import getpass
from paramiko import SSHException
import sys

password = getpass()
change_type = input('change or rollback: ').lower()
args = {'username': 'krrichar', 'password': password,
        'device_type': 'cisco_nxos'}

hosts = ['us6645ny-core-vdc1', 'us6645ny-core-vdc2',
         'us6647ny-core-vdc1', 'us6647ny-core-vdc2',
         'us9485ne-core-vdc1', 'us9485ne-core-vdc2']

wdc = {'vlan_id': '900', 
       'vlan_name': 'VL900_WDC_PROD_128.1.6.5/24', 
       'interfaces': 'interface Ethernet5/8'}

hdc = {'vlan_id': '900', 
       'vlan_name': 'VL900_HDC_PROD_128.1.6.5/24',
       'interfaces': 'interface Ethernet5/25'}

odc = {'vlan_id': '900', 
       'vlan_name': 'VL900_ODC_PROD_128.1.6.5/24',
       'interfaces': 'interface Ethernet5/25'}


def main():

    def change(num, name, interface):
        net_connect = ConnectHandler(host, session_log=host, **args)
        print(net_connect.find_prompt())
        net_connect.send_command('show run')
        precheck = net_connect.send_command('show vlan id {}'.format(num))
        if 'active' in precheck:
            print('\n\t## vlan already exists ##')
            sys.exit()
        net_connect.send_config_set(['vlan {}'.format(num),
                                     'name {}'.format(name),
                                     'interface {}'.format(interface),
                                     'switchport trunk allowed vlan add {}'.format(num)])
        postcheck = net_connect.send_command('show vlan id {}'.format(num))
        print(postcheck)
        net_connect.disconnect()

    def rollback(num, interface):
        net_connect = ConnectHandler(host, session_log=host, **args)
        print(net_connect.find_prompt())
        net_connect.send_command('show run')
        precheck = net_connect.send_command('show vlan id {}'.format(num))
        if 'not found' in precheck:
            print('\n\t## vlan is not present ##')
            sys.exit()
        net_connect.send_config_set(['no vlan {}'.format(num),
                                     'interface {}'.format(interface),
                                     'switchport trunk allowed vlan remove {}'.format(num)])
        postcheck = net_connect.send_command('show vlan id {}'.format(num))
        print(postcheck)
        net_connect.disconnect()

    for host in hosts:
        try:  # webster
            if ('6645ny' in host) and (change_type == 'change'):
                change(num=wdc['num'], name=wdc['name'], interface=wdc['interfaces'])
            elif ('6645ny' in host) and (change_type == 'rollback'):
                rollback(num=wdc['num'], interface=wdc['interfaces'])
        except (EOFError, SSHException) as error:
            print(error, '\n\t## webster changes unsuccessful ##')
        try:  # henrietta
            if ('6647ny' in host) and (change_type == 'change'):
                change(num=hdc['num'], name=hdc['name'], interface=hdc['interfaces'])
            elif ('6647ny' in host) and (change_type == 'rollback'):
                rollback(num=hdc['num'], interface=hdc['interfaces'])
        except (EOFError, SSHException) as error:
            print(error, '\n\t## henrietta changes unsuccessful ##')
        try:  # omaha
            if ('9485ne' in host) and (change_type == 'change'):
                change(num=odc['num'], name=odc['name'], interface=odc['interfaces'])
            elif ('9485ne' in host) and (change_type == 'rollback'):
                rollback(num=odc['num'], interface=odc['interfaces'])
        except (EOFError, SSHException) as error:
            print(error, '\n\t## omaha changes unsuccessful ##')

        print('\n\t## changes complete for {} ##'.format(host))


if __name__ == '__main__':
    main()
