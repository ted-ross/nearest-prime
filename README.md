# Skupper Multi-Site Load Balancing Demonstration

## Overview
This project demonstrates how Red Hat Application Interconnect (RHAI) can be used to integrate databases and client applications with globally distributed services. The demonstration highlights some important characteristics of RHAI such as:
1. Integration of VM or bare metal-hosted databases with Kubernetes-based applications.
2. Simplified multi-site application integration.
3. Geolocation hosting flexibility
4. Global cost-based routing

The project deploys a database on to a bare metal serer (your laptop), and a front end that is globally distributed across two OpenShift clusters. The final component is a work scheduler/load generator that you will run manually on your laptop. (Note: You could easily extend this to use a second VM.) The load generator is controlled via `curl` requests. 

The load generator requests the front end to calculate a nearest prime number to the number that is supplied. The front end then updates the on-premises database with the result. Prime numbers were chosen because the calculation can vary from very fast to being very computationally intensive. This introduces some randomness in the front-end's response time and thus demonstrates some important load balancing features of RHAI.

<img src="./docs/images/deployment-architecture.png" alt="drawing" width="800"/>

## Demo Setup Sequence

### Set up the DMZ sites
Begin by establishing your namespace prefix (default is `npdemo`):
```
export NP_NAMESPACE_PREFIX=mydemo
```

Use the `dmz-setup` script to create the two sites, create access-tokens for each site, and connect the two DMZ sites together:
```
dmz-setup
```

Note that some of the scripts place token files into the current working directory and other scripts use the token files from the current working directory.  Make sure that while working with different cloud environments, you are running the scripts from the same working directory.

### Set up the remote processing sites
For each remote processing site, use the `kubesite-setup` script to establish a site in the current context and namespace of a kubernetes cluster:
```
kubesite-setup <site-name>
```

When it is time to deploy the nearestprime workload on this site, use the following script to deploy the container and to wire it properly into the Skupper network:

```
np-deploy
```

You may set up more than one remote processing site.  Note that the generated access tokens have a use limit of 10 sites and a time window of 1 hour.  If you attempt to set up more than 10 sites or wait longer than an hour to do so, you will be unable to create a site.  You can, of course, modify the example YAML in the access-grants to change the limit and time window.

### Set up the on-premesis kubernetes site
Note that this step is optional.  Use it only if you wish to demonstrate on-prem operation of the nearestprime workload.

In your on-prem kubernetes environment, set up the site:
```
onprem-setup <site-name>
```

To deploy the workload here, use
```
np-deploy
```

### Set up the bare-metal access from Podman
To create a podman site that connects to the DMZ sites and, if you created it, the on-premesis site:
```
podman-setup
```

This script will create a non-kubernetes Skupper site that connects into the network.

It expects Postgres to be running on localhost at port 5432.  If your environment is different (i.e. different port or your database is on another host), make the appropriate host and port modifications in the `Connector` custom resource.

This script will also open a socket on localhost for port 8000 that can be used by the LoadGen program to request processing.

### Cleaning up demo articfacts
Each `*-setup` script has a corresponding `*-clean` script.  The clean scripts remove all of the articafts that were created by the setup scripts and the `np-deploy` script if it was used in a particular environment.

## Interesting demonstration sequences
There are a number of interesting scenarios that can be demonstrated using the scripts and components in this project.

### Workload migration from on-prem to public-cloud
To demonstrate migration, begin with the nearestprime workload deployed only in the `onprem` site.  While the demo is operating, use `np-deploy` to deploy the workload to one or more external sites.

If the offered load is sufficiently high, some of the work will spill over into the public cloud spaces, if the offered load is small (around 1), the work will remain local on the `onprem` site.  In either case, the nearestprime deployment can be scaled to zero in the `onprem` site:
```
kubectl scale deployment nearestprime --replicas=0
```
Once this is done, observe that all of the work is now being handled by the off-prem processes.

### Load balancing and redundancy across different providers/availability-zones
In this scenario, there is no need to create an on-prem site.  Instead, create a number of external sites that run in heterogeneous environments.  These could be different availbility zones for a single provider, different cloud providers altogether, and/or a mixture of private and public environments.

Sites can be added, removed, and scaled while the demo runs.
