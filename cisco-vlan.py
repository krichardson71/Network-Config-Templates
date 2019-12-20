#!/usr/bin/python
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler
from getpass import getpass

change = input('change or rollback: ')
password = getpass()

hosts = ['router-tstbr-rt02']

vlans = [{'name': 'Test VLAN 126', 'id': '126'},
         {'name': 'Test VLAN 127', 'id': '127'}]

interfaces = ['ethernet1/3']


def create_vlan():
    for host in hosts:
        args = {
            'username': 'krrichar',
            'password': password,
            'device_type': 'cisco_ios',
            'session_log': host,
        }
        net_connect = ConnectHandler(host, **args)
        net_connect.send_command('show run')
        for vlan in vlans:
            verify = net_connect.send_command(f'show vlan id {vlan["id"]}')
            if 'not found in current VLAN database' in verify:
                vlan_cmd = net_connect.send_config_set([f'vlan {vlan["id"]}',
                                                        f'name {vlan["name"]}'])
                if 'Invalid' in vlan_cmd:
                    print(f'vlan {vlan["id"]} syntax incorrect for {host}')
                    break
                else:
                    for interface in interfaces:
                        int_cmd = net_connect.send_config_set([f'interface {interface}',
                                                                f'switchport trunk allowed vlan add {vlan["id"]}'])
                        if 'Invalid' in int_cmd:
                            print(f'interface {interface} configuration is invalid for host {host}')
                            break
                        else:
                            print(f'vlan creation successful for vlan {vlan["id"]} on device {host}')
            else:
                print(f'vlan creation failed for vlan {vlan["id"]} on device {host}...vlan may already exist')
                break
            verify = net_connect.send_command(f'show vlan id {vlan["id"]}')
            print(verify)


def remove_vlan():
    for host in hosts:
        args = {
            'username': 'krrichar',
            'password': password,
            'device_type': 'cisco_ios',
            'session_log': host,
        }
        net_connect = ConnectHandler(host, **args)
        for vlan in vlans:
            net_connect.send_config_set(f'no vlan {vlan["id"]}')
            for interface in interfaces:
                net_connect.send_config_set([f'interface {interface}',
                                             f'switchport trunk allowed vlan remove {vlan["id"]}'])


if __name__ == '__main__':
    if change == 'change':
        create_vlan()
    elif change == 'rollback':
        remove_vlan()
