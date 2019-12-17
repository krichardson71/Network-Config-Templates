# !/usr/bin/python
# -*- coding: utf-8 -*-

from getpass import getpass
import requests
import sys
import time
from f5.bigip import ManagementRoot
from f5.utils.responses.handlers import Stats
from icontrol.exceptions import iControlUnexpectedHTTPError

change = input('Change or Rollback? ').lower()

password = getpass()
requests.packages.urllib3.disable_warnings()
mgmt = ManagementRoot(sys.argv[1], 'admin', password)
ltm = mgmt.tm.ltm

# Node Details

nodes = [{'name': 'sdk-node', 'address': '10.30.32.99'},
         {'name': 'sdk-node2', 'address': '10.30.32.100'}]

# Pool Details

pool_name = 'sdk-pool'
member_port = '80'
monitor = 'gateway_icmp'

# Virtual Server Details

vs_name = 'sdk-virtual'
vip = '192.168.100.10'
port = '80'
profiles = [{'name': 'f5-tcp-wan', 'context': 'clientside'},
            {'name': 'f5-tcp-lan', 'context': 'serverside'},
            {'name': 'serverssl', 'context': 'serverside'},
            {'name': 'http'}]


def ltm_build():
    if change == 'change':
        try:
            ltm.pools.pool.create(name=pool_name, monitor=monitor)
            pool = ltm.pools.pool.load(name=pool_name)

            for node in nodes:
                ltm.nodes.node.create(partition='Common',
                                      name=node['name'], address=node['address'])
                pool.members_s.members.create(partition='Common',
                                              name=node['name'] + ':' + member_port)

            params = {
                'name': vs_name,
                'destination': f'{vip}:{port}',
                'mask': '255.255.255.255',
                'pool': pool_name,
                'profiles': profiles,
                'partition': 'Common',
                'sourceAddressTranslation': {'type': 'automap'},
            }

            ltm.virtuals.virtual.create(**params)
            print('Build Complete...', '\n')

            time.sleep(1)

            virtual = ltm.virtuals.virtual.load(partition='Common', name=vs_name)
            virtual_stats = Stats(virtual.stats.load())
            pool_stats = Stats(pool.stats.load())
            print(f'Pool {pool_name} status:', pool_stats.stat.status_availabilityState['description'])
            print(f'Virtual Server {vs_name} status:', virtual_stats.stat.status_availabilityState['description'])

        except iControlUnexpectedHTTPError:
            print('Duplicate Objects Exist...Build Failed')
            sys.exit()

    elif change == 'rollback':
        try:
            virtual = ltm.virtuals.virtual.load(
                partition='Common', name=vs_name)
            virtual.delete()

            pool = ltm.pools.pool.load(name=pool_name)
            pool.delete()

            for node in nodes:
                ltm.nodes.node.load(
                    partition='Common', name=node['name']).delete()
            print('Rollback Complete...')

        except iControlUnexpectedHTTPError:
            print(
                'One of more objects couldn\'t be found...Rollback Failed...')
            sys.exit()


if __name__ == '__main__':
    ltm_build()
