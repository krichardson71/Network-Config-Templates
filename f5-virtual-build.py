#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from f5.bigip import ManagementRoot
from getpass import getpass

change = input('change or rollback: ').lower()
password = getpass()
requests.packages.urllib3.disable_warnings()

hosts = ['us6645ny-ppcore-ltm-n2a',
         'us6645ny-ppcore-ltm-n',
         'us6645ny-ppcore-ltm-perf']

for host in hosts:
    mgmt = ManagementRoot(host, 'admin', password)
    ltm = mgmt.tm.ltm
    if change == 'change':

        def ltm_virtual(name=str(), vip=str(), port=str(), pool_name=str()):

            params = {
                'name': name,
                'destination': vip + ':' + port,
                'mask': '255.255.255.255',
                'pool': pool_name,
                'profiles': [{'name': 'f5-tcp-wan',
                              'context': 'clientside'},
                             {'name': 'f5-tcp-lan',
                              'context': 'serverside'}],
                'partition': 'Common',
                'sourceAddressTranslation': {'type': 'automap'},
            }
            ltm.virtuals.virtual.create(**params)


        if host == 'us6645ny-ppcore-ltm-n2a':
            servers = [{'name': 'vs-kafka-schemaregR-8081-pyx-n2a-wdc', 'vip': '10.3.7.124',
                        'pool': 'pool-kafka-schemareg-8081-pyx-n2a-wdc'},
                       {'name': 'vs-kafka-schemaregW-8081-pyx-n2a-wdc', 'vip': '10.3.7.125',
                        'pool': 'pool-kafka-schemareg-8081-pyx-n2a-wdc'}]
            for server in servers:
                ltm_virtual(name=server['name'], vip=server['vip'], port='8081',
                            pool_name=server['pool'])
        elif host == 'us6645ny-ppcore-ltm-n':
            servers = [{'name': 'vs-kafka-schemaregR-8081-pyx-n1-wdc', 'vip': '10.3.9.71',
                        'pool': 'pool-kafka-schemareg-8081-pyx-n1-wdc'},
                       {'name': 'vs-kafka-schemaregW-8081-pyx-n1-wdc', 'vip': '10.3.9.72',
                        'pool': 'pool-kafka-schemareg-8081-pyx-n1-wdc'},
                       {'name': 'vs-kafka-schemaregR-8081-pyx-n0-wdc', 'vip': '10.3.9.73',
                        'pool': 'pool-kafka-schemareg-8081-pyx-n0-wdc'},
                       {'name': 'vs-kafka-schemaregW-8081-pyx-n0-wdc', 'vip': '10.3.9.76',
                        'pool': 'pool-kafka-schemareg-8081-pyx-n0-wdc'}]
            for server in servers:
                ltm_virtual(name=server['name'], vip=server['vip'], port='8081',
                            pool_name=server['pool'])
        elif host == 'us6645ny-ppcore-ltm-perf':
            servers = [{'name': 'vs-kafka-schemaregR-8081-pyx-pf-wdc', 'vip': '10.3.15.38',
                        'pool': 'pool-kafka-schemareg-8081-pyx-pf-wdc'},
                       {'name': 'vs-kafka-schemaregW-8081-pyx-pf-wdc', 'vip': '10.3.15.39',
                        'pool': 'pool-kafka-schemareg-8081-pyx-pf-wdc'}]
            for server in servers:
                ltm_virtual(name=server['name'], vip=server['vip'], port='8081',
                            pool_name=server['pool'])

    if change == 'rollback':

        if host == 'us6645ny-ppcore-ltm-n2a':
            servers = ['vs-kafka-schemaregR-8081-pyx-n2a-wdc',
                       'vs-kafka-schemaregW-8081-pyx-n2a-wdc']
            for server in servers:
                virtual = ltm.virtuals.virtual.load(partition='Common',
                                                    name=server)
                virtual.delete()

        elif host == 'us6645ny-ppcore-ltm-n':
            servers = ['vs-kafka-schemaregR-8081-pyx-n1-wdc',
                       'vs-kafka-schemaregW-8081-pyx-n1-wdc',
                       'vs-kafka-schemaregR-8081-pyx-n0-wdc',
                       'vs-kafka-schemaregW-8081-pyx-n0-wdc']
            for server in servers:
                virtual = ltm.virtuals.virtual.load(partition='Common',
                                                    name=server)
                virtual.delete()

        elif host == 'us6645ny-ppcore-ltm-perf':
            servers = ['vs-kafka-schemaregR-8081-pyx-pf-wdc',
                       'vs-kafka-schemaregW-8081-pyx-pf-wdc']
            for server in servers:
                virtual = ltm.virtuals.virtual.load(partition='Common',
                                                    name=server)
                virtual.delete()
