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

hosts = ['us6645ny-ppcore-vdc1',
         'us6647ny-ppcore-vdc1']

wdc = {'num': '900',
       'name': 'VL900_WDC_N2A_128.1.6.5/24',
       'interfaces': 'Ethernet1/3, Ethernet1/6, Ethernet1/10-13,\
                      Ethernet5/3, Ethernet5/6, Ethernet5/10-13'}
hdc = {'num': '900',
       'name': 'VL900_HDC_N2A_128.1.6.5/24',
       'interfaces': 'Ethernet1/3, Ethernet1/6-7, Ethernet1/10, Ethernet1/12, Ethernet1/15,\
                      Ethernet5/3, Ethernet5/6-7, Ethernet5/10, Ethernet5/12, Ethernet5/15'}


def main():

    def change(num, name, interface):
        """
        @param num: vlan id
        @param name: vlan name
        @param interface: trunk interface(s) to add vlan
        @return: None

        """
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
        net_connect.send_command('copy running-config startup-config')
        net_connect.disconnect()

    def rollback(num, interface):
        """
        @param num: vlan id
        @param interface: trunk interface(s) to add vlan
        @return: None

        """
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
        net_connect.send_command('copy running-config startup-config')
        net_connect.disconnect()

    for host in hosts:

        #  webster
        try:
            if ('6645ny' in host) and (change_type == 'change'):
                change(num=wdc['num'], name=wdc['name'], interface=wdc['interfaces'])
            elif ('6645ny' in host) and (change_type == 'rollback'):
                rollback(num=wdc['num'], interface=wdc['interfaces'])
        except (EOFError, SSHException) as error:
            print(error, '\n\t## webster changes unsuccessful ##')

        #  henrietta
        try:
            if ('6647ny' in host) and (change_type == 'change'):
                change(num=wdc['num'], name=wdc['name'], interface=wdc['interfaces'])
            elif ('6647ny' in host) and (change_type == 'rollback'):
                rollback(num=hdc['num'], interface=hdc['interfaces'])
        except (EOFError, SSHException) as error:
            print(error, '\n\t## henrietta changes unsuccessful ##')

        print('\n\t## changes complete for {} ##'.format(host))


if __name__ == '__main__':
    main()
