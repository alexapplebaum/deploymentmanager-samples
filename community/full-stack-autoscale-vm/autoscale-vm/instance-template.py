# pylint: disable=W,C,R

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_config(context):
    """Generate instance template resource configuration."""

    access_configs = []
    if context.properties['provisionPublicIp']:
        access_configs = [{'name': 'Management NAT', 'type': 'ONE_TO_ONE_NAT'}]

    resources = [{
        'name': context.env['name'],
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
                'tags': {
                    'items': ['mgmtfw-' + context.properties['uniqueString'], 'appfw-' + context.properties['uniqueString']]
                },
                'machineType': context.properties['instanceType'],
                'disks': [{
                    'deviceName': 'boot',
                    'type': 'PERSISTENT',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': ''.join([COMPUTE_URL_BASE,
                                                context.properties['imageName'],
                                                ])
                    }
                }],
                'networkInterfaces': [{
                    'network': context.properties['networkSelfLink'],
                    'subnetwork': context.properties['subnetSelfLink'],
                    'accessConfigs': access_configs
                }],
                'metadata': {
                    'items': [{
                        'key': 'startup-script',
                        'value': ''.join(['#!/bin/bash\n',
                                          'yum -y install docker\n',
                                          'service docker start\n',
                                          'docker run --name myapp -p 80:80 -p 443:443 -d ',
                                          context.properties['appContainerName']])
                    },
                        {
                        'key': 'unique-string',
                        'value': context.properties['uniqueString']
                    },
                        {
                        'key': 'region',
                        'value': context.properties['region']
                    }]
                }
            }
        }
    }]

    return {'resources': resources}
