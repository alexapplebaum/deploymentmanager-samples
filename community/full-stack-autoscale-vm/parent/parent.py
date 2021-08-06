"""Creates the Deployment"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

# pylint: disable=C0301


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix

# pylint: disable=C0301


def create_network_deployment(context):
    """ Create template deployment """
    deployment = {
        'name': 'network',
        'type': '../network/network.py',
        'properties': {
            'name': 'network0',
            'uniqueString': context.properties['uniqueString'],
            'subnets': [{
                'description': 'Subnetwork used for management',
                'name': 'mgmt1',
                'region': context.properties['region'],
                'ipCidrRange': '10.0.0.0/24'
            },
                {
                'description': 'Subnetwork used for application services',
                'name': 'application1',
                'region': context.properties['region'],
                'ipCidrRange': '10.0.1.0/24'
            }]
        }
    }
    return deployment

# pylint: disable=C0301


def create_autoscale_vm_deployment(context):
    """ Create template deployment """
    deployment = {
        'name': 'autoscale-vm',
        'type': '../autoscale-vm/autoscale-vm.py',
        'properties': {
            'appContainerName': context.properties['appContainerName'],
            'availabilityZone': context.properties['availabilityZone'],
            'coolDownPeriodSec': context.properties['coolDownPeriodSec'],
            'imageName': context.properties['imageName'],
            'instanceTemplateVersion': context.properties['instanceTemplateVersion'],
            'instanceType': context.properties['instanceType'],
            'maxNumReplicas': context.properties['maxNumReplicas'],
            'minNumReplicas': context.properties['minNumReplicas'],
            # https://github.com/GoogleCloudPlatform/deploymentmanager-samples/issues/39#issuecomment-351810889
            'networkSelfLink': '$(ref.network.selfLink)',
            # 'networkSelfLink': 'projects/yourproject/global/networks/uniqueStr-network0',
            'project': context.env['project'],
            'provisionPublicIp': context.properties['provisionPublicIp'],
            'region': context.properties['region'],
            'subnetSelfLink': '$(ref.network.subnets.' + context.properties['uniqueString'] + '-mgmt1.selfLink)',
            # 'subnetSelfLink': 'projects/yourprojectregions/us-west1/subnetworks/uniqueStr-mgmt1',
            'uniqueString': context.properties['uniqueString'],
            'utilizationTarget': context.properties['utilizationTarget']
        }
    }
    return deployment

# pylint: disable=C0301


def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
        context.env['name']
    deployment_name = generate_name(context.properties['uniqueString'], name)

    resources = [create_network_deployment(context)] + \
                [create_autoscale_vm_deployment(context)]

    outputs = [
        {
            'name': 'deploymentName',
            'value': deployment_name
        }
    ]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
