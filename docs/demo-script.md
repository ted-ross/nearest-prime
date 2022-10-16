# Demo Script

## Deploy RHAI to all Namespaces

### OpenShift Local
```
skupper init --site-name on-prem
```

### Remote Site 1
```
skupper init --site-name site-1
```

### Remote Site 2
```
skupper init --site-name site-2
```

Check the install status for each site using `skupper status`.
```
$ skupper status
Skupper is enabled for namespace "nearest-prime" with site name "ON-PREM" in interior mode. It is not connected to any other sites. It has no exposed services.
The site console url is:  https://skupper-nearest-prime.apps-crc.testing
The credentials for internal console-auth mode are held in secret: 'skupper-console-users'
$
```

## Create the RHAI Application Network
The on-prem OpenShift Local environment is not externally routable, but the RHPDS andf Open-TLC environments are routable. At each of the routable site, create a token:

```
skupper token create --token-type cert opentlc-token.yaml
Connection token written to remote1-token.yaml 

```

```
$ skupper token create --token-type cert rhpds-token.yaml
Connection token written to remote2-token.yaml 
```

Import the tokens into the On-Premises OpenShift on OpenShift Local uaing the `skupper link create <token filename>` command:
```
ONPREM$ skupper link status
There are no links configured or active

ONPREM$ skupper link create remote1-token.yaml 

Site configured to link to skupper-inter-router-nearest-prime.apps.cluster-8q9n5.8q9n5.sandbox464.opentlc.com:443 (name=link1)
Check the status of the link using 'skupper link status'.

ONPREM$ skupper link create remote2-token.yaml

Site configured to link to skupper-inter-router-nearest-prime.apps.cluster-6lg79.6lg79.sandbox507.opentlc.com:443 (name=link2)
Check the status of the link using 'skupper link status'.

ONPREM$ skupper link status
Link link1 is active
Link link2 is active
```

At each site run the command `skupper status`. Observe that each site is connected to two other sites, and the remote sites are connected to one indirectly:

```
REMOTE1$ skupper status
Skupper is enabled for namespace "nearest-prime" with site name "site-1" in interior mode. It is connected to 2 other sites (1 indirectly). It has no exposed services.
The site console url is:  https://skupper-nearest-prime.apps.cluster-8q9n5.8q9n5.sandbox464.opentlc.com
The credentials for internal console-auth mode are held in secret: 'skupper-console-users'
$
```

### Create the Gateway Router
Finally you need to add the on-premises database to the network. 

```
skupper gateway expose db 127.0.0.1 5432 --type podman
```

Once the gateway has been created successfully, look at the services and pods:

```
oc get svc,pods
```
Observe that the db service has not pods, and the ip address is a local ip adress of the cluster. The RHAI router handles routing a service request over the RHAI network to the on premises local ip address and port.   

```
ONPREM$ oc get svc
NAME                   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)               AGE
db                     ClusterIP   10.217.4.144   <none>        5432/TCP              33s
skupper                ClusterIP   10.217.5.195   <none>        8080/TCP,8081/TCP     7m25s
skupper-router         ClusterIP   10.217.5.210   <none>        55671/TCP,45671/TCP   7m27s
skupper-router-local   ClusterIP   10.217.4.250   <none>        5671/TCP              7m27s
ONPREM$ 
```

```
IBMSYD$ oc get svc,pods
NAME                           TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)               AGE
service/db                     ClusterIP   172.21.185.7   <none>        5432/TCP              25s
service/skupper                ClusterIP   172.21.227.9   <none>        8080/TCP,8081/TCP     4m4s
service/skupper-router         ClusterIP   172.21.49.45   <none>        55671/TCP,45671/TCP   4m5s
service/skupper-router-local   ClusterIP   172.21.7.50    <none>        5671/TCP              4m6s

NAME                                             READY   STATUS    RESTARTS   AGE
pod/skupper-router-5cdf8bb5cb-w79k5              2/2     Running   0          4m5s
pod/skupper-service-controller-6d977db56-nph9n   1/1     Running   0          4m3s
IBMSYD$ 
```

## Deploy the Remote Applications
At each of the remote sites, create the nearest prime deployment:

```
oc apply -f nearestprime.yaml
```

```
IBMSYD$ oc get svc,pods
NAME                           TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)               AGE
service/db                     ClusterIP   172.21.185.7   <none>        5432/TCP              6m58s
service/skupper                ClusterIP   172.21.227.9   <none>        8080/TCP,8081/TCP     10m
service/skupper-router         ClusterIP   172.21.49.45   <none>        55671/TCP,45671/TCP   10m
service/skupper-router-local   ClusterIP   172.21.7.50    <none>        5671/TCP              10m

NAME                                             READY   STATUS    RESTARTS   AGE
pod/nearestprime-d78ccc599-94nrg                 1/1     Running   0          74s
pod/skupper-router-5cdf8bb5cb-w79k5              2/2     Running   0          10m
pod/skupper-service-controller-6d977db56-nph9n   1/1     Running   0          10m
IBMSYD$ 
```

Observe that there is a pod but no service created for the deployment.

Now look at the services and pods on the on-premises cluster:
```
ONPREM$ oc get svc,pods
NAME                           TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)               AGE
service/db                     ClusterIP   10.217.4.144   <none>        5432/TCP              9m59s
service/skupper                ClusterIP   10.217.5.195   <none>        8080/TCP,8081/TCP     16m
service/skupper-router         ClusterIP   10.217.5.210   <none>        55671/TCP,45671/TCP   16m
service/skupper-router-local   ClusterIP   10.217.4.250   <none>        5671/TCP              16m

NAME                                              READY   STATUS    RESTARTS   AGE
pod/skupper-router-55f4498857-k6zg2               2/2     Running   0          16m
pod/skupper-service-controller-64659988b8-j6985   1/1     Running   0          16m
```

Observe that there is no service for the nearestprime deployment at the remote site.

Now, at each of the remote clusters, we want to expose the nearestprime deployment so that it is available elsewhere. At each remote site type `skupper expose deployment nearestprime --port 8000 --protocol http` and press Enter.

```
IBMSYD$ skupper expose deployment nearestprime --port 8000 --protocol http
deployment nearestprime exposed as nearestprime
```

Examine the services and pods on the on-premises cluster. Type `oc get svc,pods` and press Enter.

```
ONPREM$ oc get svc,pods
NAME                           TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)               AGE
service/db                     ClusterIP   10.217.4.144   <none>        5432/TCP              12m
service/nearestprime           ClusterIP   10.217.4.15    <none>        8000/TCP              2m27s
service/skupper                ClusterIP   10.217.5.195   <none>        8080/TCP,8081/TCP     19m
service/skupper-router         ClusterIP   10.217.5.210   <none>        55671/TCP,45671/TCP   19m
service/skupper-router-local   ClusterIP   10.217.4.250   <none>        5671/TCP              19m

NAME                                              READY   STATUS    RESTARTS   AGE
pod/skupper-router-55f4498857-k6zg2               2/2     Running   0          19m
pod/skupper-service-controller-64659988b8-j6985   1/1     Running   0          19m
```

Observe that the remote service is now published on premises but there are no pods for the service. RHAI will handle routing any request to the service over the RHAI network to the remote service and pod.

No matter how many remote sites expose the nearestprime service, there will only be one instance on-premises. This is because the service is an any-cast address. RHAI will handle routing the service request across the remote implementations.

**Note:** If you want to expose them individually then you would use unique names (such as nearestprime-ibmdc, nearestprime-awseur).

Repeat this for each remote site and observe that the service exists everywhere.

### Set up Gateway Forwarding
One last thing to set up is the gateway forwarding. This enables an on premises application to access the services published by the gateway.
```
ONPREM$ skupper gateway forward nearestprime 8000

2022/07/18 14:32:11 CREATE io.skupper.router.httpListener rh-brbaker-bakerapps-net-bryon-ingress-nearestprime:8000 map[address:nearestprime:8000 name:rh-brbaker-bakerapps-net-bryon-ingress-nearestprime:8000 port:8000 protocolVersion:HTTP1 siteId:12f4cb92-b361-457b-8362-1b77f9a6e9d5]
```

### Review all of the connectivity details
<span style="color:yellow">REVISIT: Review this content again.</span>

The final step is to review the entire network configuration. You run this at any site, but for this demonstartion we will use on-premises. Type the command `skupper network status` and press Enter.

Observe 
'''
ONPREM$ skupper network status
Sites:
├─ [local] 2360822 - on-prem 
│  URL: skupper-inter-router-nearestprime.apps-crc.testing
│  mode: interior
│  name: on-prem
│  namespace: nearestprime
│  sites linked to: d4c2e69-remote-1
│  version: 1.0.2
│  ╰─ Services:
│     ├─ name: nearestprime
│     │  address: nearestprime: 8000
│     │  protocol: http
│     ╰─ name: db
│        address: db: 5432
│        protocol: tcp
╰─ [remote] d4c2e69 - remote-1
   URL: skupper-inter-router-nearestprime.violet-cluster-new-2761a99850dd8c23002378ac6ce7f9ad-0000.au-syd.containers.appdomain.cloud
   name: remote-1
   namespace: nearestprime
   version: 1.0.2
   ╰─ Services:
      ├─ name: nearestprime
      │  address: nearestprime: 8000
      │  protocol: http
      │  ╰─ Targets:
      │     ╰─ name: nearestprime-d78ccc599-k44x7
      ╰─ name: db
         address: db: 5432
         protocol: tcp

'''

# Installation and Configuration Finished

**Congratulations, you have now:**
1. Deployed the RHAI routers to all the application namespaces.
2. Created the application network.
3. Deployed the application
4. Advertised the application's endpoint to all namspaces in the RHAI network.

At this point in the story you have set up the RHAI network amd deployed all the applications. As you did this you highlighted how you could integrate with unroutable networks and with applications outside OpenShift.

You are now ready to test the configuration.


## Load Generator

The load generator is located in under the `components` directory.  

```
cd components/load-gen
```

Build and run the load generaor. Note: The first time you run this it will take a while to download all the maven repositories.

```
ONPREM$ ./mvnw quarkus:dev
Warning: JAVA_HOME environment variable is not set.
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------------< io.skupper:load-gen >-------------------------
[INFO] Building load-gen 1.0-SNAPSHOT
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- quarkus-maven-plugin:1.2.1.Final:dev (default-cli) @ load-gen ---
[INFO] Nothing to compile - all classes are up to date
OpenJDK 64-Bit Server VM warning: Options -Xverify:none and -noverify were deprecated in JDK 13 and will likely be removed in a future release.
Listening for transport dt_socket at address: 5005
2022-07-17 21:14:24,094 INFO  [io.quarkus] (main) load-gen 1.0-SNAPSHOT (running on Quarkus 1.2.1.Final) started in 0.737s. Listening on: http://0.0.0.0:8080
2022-07-17 21:14:24,105 INFO  [io.quarkus] (main) Profile dev activated. Live Coding activated.
2022-07-17 21:14:24,105 INFO  [io.quarkus] (main) Installed features: [cdi, rest-client, resteasy, resteasy-jsonb, vertx]
```

The load generator is now running and listening for instruction on `http://localhost:8080`. You will use surl to control the load generator:

### Generate some load

The load generator is controlled by curl requests.
```
curl http://localhost:8080/set_load/0
```

Generate 10 parallel requests.
```
curl http://localhost:8080/set_load/10
```
This will continue to generate 10 parallel requests until you set the load to zero. **Note:** You should never need to increase the load above 10.


To stop the load type the following command:
```
curl http://localhost:8080/set_load/0
```

Query the database contents and observe that the load balancing is not round robin. In ```pgadmin4```, query the database:

```
select * from work where nearprime is not null
```

It will choose the service instance that has the lowest backlog. It directs trafic to the router that is most likely to process the request in the shortest amount of time.

No need for circuit breaker functionality, it is built into the network.

Interesting use cases: You can use this to do cost-based bursting and burst to the lowest-cost cloud.

### Try Scaling the Application at the Slowest Site
We expect to see the load balancing change slightly due to the increased capacity at the slowest remote site. (Note: This may not always work because it depends upon the network latency.)

<span style="color:yellow">REVISIT: Write this section.</span>

# End of Demo Script

Return to [Main Index](../README.md)
