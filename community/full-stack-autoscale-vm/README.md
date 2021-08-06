# Instance Group Updater Example

This example creates an full stack, network + instance group and is loosely based on the igm-updater example in main examples/v2 dir. 

The example consists of:

*   3 python templates
    *   parent.py - the top level template
    *   network.py
        *   Creates the network (and subnet)
    *   austcale-vm.py
        *   Creates the instance templates, using instance-template.py
        *   Creates the instance group
        *   On update, update the instance group
*   a schema file for the top level python template
    *   Defines the required inputs and defaults for the optional ones
        properties.
*   2 yaml files - used to test the templates with rolling out different images


To perform a rolling update on an instance group, below resources are needed:

1.  the instance group
1.  the current (ie new) instance template

The update will take several minutes to run, so be patient. Running below
command to monitor the rolling updates of the instances:

```
$ gcloud compute instance-groups managed list-instances <INSTANCE_GROUP_NAME> --zone=<ZONE>
```

The parent directory also contains 2 yaml files which toggle the instance template version to trigger an update. 

To run the example use them in order.

1.  Create the deployment and deploy the debian image `gcloud deployment-manager
    deployments create MYDEPLOYMENTNAME --config parent-1.yaml`
1.  Update the deployment with ubuntu `gcloud deployment-manager deployments
    update MYDEPLOYMENTNAME --config parent-2.yaml`


Unlike the igm-update example, when the calling template uses self-link references for the network, it results in CYCLIC_REFERENCES error:

```
$ gcloud  deployment-manager deployments update myparent --config parent-2.yaml
The fingerprint of the deployment is b'OrC90UgOl7yY-lGlOMt_yA=='
Waiting for update [operation-1628281354059-5c8e9cbb3fd70-4ceff8f4-ae04ad50]...failed.                                                                        
ERROR: (gcloud.deployment-manager.deployments.update) Error in Operation [operation-1628281354059-5c8e9cbb3fd70-4ceff8f4-ae04ad50]: errors:
- code: CYCLIC_REFERENCES
  message: |
    A cycle was found during reference analysis:
    Detected cycle:
    mycyclic-network0 <- myparent-it-v-1 <- myparent-igm <- myparent-it-v-2
```