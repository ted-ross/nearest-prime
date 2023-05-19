# Nearest prime demo using skupper-ansible

This section provides an automated approach for setting up and verifying
the Nearest Prime demo using Ansible to deploy it against Kubernetes and Podman.

# Pre-requisites

You must have ansible installed.
These dependencies can be installed using pip installer:

```shell
pip install --user ansible
```

# Customizing k8s cluster and podman host

The demo is currently set to spin up two Skupper sites. One in a Kubernetes
cluster and the other one as a podman site.

You can customize the target location for the Kubernetes site, by adjusting
the `kubeconfig` and `namespace` entries in the `ansible/inventory-nearestprime-demo.yml`
inventory file.

The podman site (`rhel9` host) currently has a static ingress host defined as
`192.168.124.1`, you can also customize it by updating the inventory file.
This host is defined to be your local machine (meaning no external connection is made by Ansible),
but eventually, you can modify it to be a remote host (accessible via SSH using your
own SSH keys), by doing this:

- Comment this line: `ansible_connection: local`
- Uncomment this one: `#ansible_host: <remote_ip_addr>`
  - And set the appropriate remote IP address

# Installing the demo

Before deploying this demo, make sure to update the inventory file
`ansible/inventory-nearestprime-demo.yml` and set the:

* Ingress IP for the podman site
* Kubeconfig file location

After doing it, and eventually adjusting other parameters, just run:

```shell
make setup 
```

The setup will perform the tasks below (among others):

* Create a namespace at the Kubernetes cluster
  * Deploying the nearestprime service to it
* Run the podman containers (for DB and Load Generator)
* Initialize and link Skupper on both sites (k8s and podman)
* Define all the required Skupper services at each location

If no failure has been observed, your scenario should be up and running.

# Validate using the load generator

You can activate the load generator, by running:

`make load-gen-start`

This will run the load generator using 2 parallel instances.
If you want to run more instances, you can pass the `SIZE` of the
parallel instances to run by doing:

`make load-gen-start SIZE=10`

To stop the load generator, just run:

`make load-gen-stop`

You can also monitor the number of processed records, from the database
by running: `make monitordb`.

# Teardown

To clean up everything, just run: `make teardown`.
