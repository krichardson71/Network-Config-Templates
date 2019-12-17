#!/usr/bin/python
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler
from getpass import getpass
from paramiko import SSHException

change = input('Change or Rollback? ').lower()
password = getpass()

hosts = [
    'us6645ny-mpls-rt02',
    'us6645ny-mpls-rt06',
    'us9035oh-mpls-rt01',
    'us9035oh-mpls-rt02',
    'us0065co-mc01-rt01',
    'us0065co-mc01-rt02',
    'us0075az-mc01-rt01',
    'us0075az-mc01-rt02',
    'us0681fl-mc01-rt01',
    'us0681fl-mc01-rt02',
    ]

args = {'username': 'krrichar', 'password': password,
        'device_type': 'cisco_ios'}

cfg = ['ip access-list standard 55', '220 permit 10.25.4.79']


def snmp():
    if change == 'change':
        try:
            for host in hosts:
                net_connect = ConnectHandler(host, **args)
                output = \
                    net_connect.send_command('show ip access-list 55')
                if 'Standard' in output:
                    if '220 permit' not in output:
                        netflow = net_connect.send_config_set(cfg)
                        print(netflow)
                else:
                    print('ACL Does Not Exist or Sequence Already Exists for host -->', host)
        except (EOFError, SSHException) as error:
            print('Configuration skipped')
    elif change == 'rollback':
        try:
            for host in hosts:
                net_connect = ConnectHandler(host, **args)
                output = \
                    net_connect.send_command('show ip access-list 55')
                if 'access list' in output:
                    if '220 permit' in output:
                        netflow = net_connect.send_config_set('no', cfg[1])
                        print(netflow)
                    else:
                        net_connect.find_prompt()
                        print('ACL Does not Exist or Sequence Already Exists')
        except (EOFError, SSHException) as error:
            print('ACL Does not Exist or Sequence Already Exists')


if __name__ == '__main__':
    snmp()
