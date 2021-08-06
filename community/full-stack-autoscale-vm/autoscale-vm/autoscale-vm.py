# pylint: disable=W,C,R

"""Creates the autoscale group"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix


def create_instance_template(context, instance_template_name):
    """ Create autoscale instance template """
    instance_template = {
        'name': instance_template_name,
        'type': 'instance-template.py',
        'properties': {
            'appContainerName': context.properties['appContainerName'],
            'imageName': context.properties['imageName'],
            'instanceType': context.properties['instanceType'],
            # depends on network
            'networkSelfLink': context.properties['networkSelfLink'],
            'provisionPublicIp': context.properties['provisionPublicIp'],
            'region': context.properties['region'],
            'subnetSelfLink': context.properties['subnetSelfLink'],
            'uniqueString': context.properties['uniqueString'],
        }
    }
    return instance_template


def create_instance_group(context, instance_template_name):
    """ Create autoscale instance group """
    instance_group = {
        'name': context.env['deployment'] + '-igm',
        # 'type': 'compute.v1.instanceGroupManager',
        'type': 'compute.beta.instanceGroupManager',
        'properties': {
            'baseInstanceName': context.env['deployment'] + '-vm',
            # depends on instance template
            'instanceTemplate': '$(ref.' + instance_template_name + '.selfLink)',
            # depends on target pool
            'targetPools': ['$(ref.' + context.env['deployment'] + '-tp.selfLink)'],
            'targetSize': 2,
            'updatePolicy': {
                'type': 'PROACTIVE',
                'minimalAction': 'REPLACE'
            },
            'zone': context.properties['availabilityZone']
        }
    }
    return instance_group


def create_autoscaler(context):
    """ Create autoscaler """
    autoscaler = {
        'name': context.env['deployment'] + '-as',
        'type': 'compute.v1.autoscalers',
        'properties': {
            'zone': context.properties['availabilityZone'],
            # depends on instance group manager
            'target': '$(ref.' + context.env['deployment'] + '-igm.selfLink)',
            'autoscalingPolicy': {
                "minNumReplicas": context.properties['minNumReplicas'],
                'maxNumReplicas': context.properties['maxNumReplicas'],
                'cpuUtilization': {
                    'utilizationTarget': context.properties['utilizationTarget']
                },
                'coolDownPeriodSec': context.properties['coolDownPeriodSec']
            }
        }
    }
    return autoscaler


def create_health_check(context, source):
    """ Create health check """
    applicaton_port = str(context.properties['applicationPort'])
    applicaton_port = applicaton_port.split()[0]
    if source == "internal":
        health_check = {
            'name': context.env['deployment'] + '-' + source,
            'type': 'compute.v1.healthCheck',
            'properties': {
                'type': 'TCP',
                'tcpHealthCheck': {
                    'port': int(applicaton_port)
                }
            }
        }
    else:
        health_check = {
            'name': context.env['deployment'] + '-' + source,
            'type': 'compute.v1.httpHealthCheck',
            'properties': {
                'port': int(applicaton_port)
            }
        }

    return health_check


def create_target_pool(context):
    """ Create target pool """
    target_pool = {
        'name': context.env['deployment'] + '-tp',
        'type': 'compute.v1.targetPool',
        'properties': {
            'region': context.properties['region'],
            'sessionAffinity': 'CLIENT_IP',
            # depends on health check
            'healthChecks': ['$(ref.' + context.env['deployment'] + '-external.selfLink)'],
        }
    }
    return target_pool


def create_target_pool_outputs(context):
    """ Create target pool outputs """
    target_pool = {
        'name': 'targetPool',
        'resourceName': context.env['deployment'] + '-tp',
        # depends on target pool
        'value': '$(ref.' + context.env['deployment'] + '-tp.selfLink)'
    }
    return target_pool


def create_instance_group_output(context):
    """ Create instance group output """
    instance_group = {
        'name': 'instanceGroupName',
        'value': ''.join([COMPUTE_URL_BASE,
                          'projects/',
                          context.properties['project'],
                          '/zones/',
                          context.properties['availabilityZone'],
                          '/instanceGroups/',
                          context.env['deployment'],
                          '-igm'
                          ])
    }
    return instance_group


def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
        context.env['name']
    autoscale_deployment_name = generate_name(
        context.properties['uniqueString'], name)
    instance_template_name = context.env['deployment'] + \
        '-it-v-' + \
        str(context.properties['instanceTemplateVersion'])

    resources = []
    resources = resources + [create_instance_template(context, instance_template_name)] + \
        [create_target_pool(context)] + \
        [create_health_check(context, 'external')] + \
        [create_instance_group(context, instance_template_name)] + \
        [create_autoscaler(context)]

    outputs = [
        {
            'name': 'instanceGroupName',
            'value': autoscale_deployment_name
        }
    ]

    outputs = outputs + \
        [create_instance_group_output(
            context), create_target_pool_outputs(context)]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }
