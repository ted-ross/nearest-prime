# Application Interconnect Multi-Site Load Balancing Demonstration
## Overview
This project demonstrates how Red Hat Application Interconnect (RHAI) can be used to integrate databases and client applications with globally distributed services. The demonstration highlights some important characteristics of RHAI such as:
1. Integration of VM or bare metal-hosted databases with Kubernetes-based applications.
2. Simplified multi-site application integration.
3. Geolocation hosting flexibility
4. Global cost-based routing

Note: Red Hat Application Interconnect is based on the updstream opensource project "Skupper."

## Prerequisites
This example has been tested using Fedora 36 running OpenShift Local (previsously known as Code Ready Containers) as the "on premises cluster."

In all, the demonstration uses three clusters. one on premises, and two remote clusters. You can get away with one external cluster and run two projects (name spaces) but be careful of the context switching.

Note: There should be no reason this does not work on macOS or other linux distributions, but you will need to replace podman with docker in the scripts. This example will also work with any other Kubernetes distribution such as EKS and GKE after some very monor tweaks to replace the *oc* commands with *kubectl* commands.

### OpenShift Version:
The demonstration has been developed using OpenShift 4.10, but this should work on any OpenShift 4 verison with no chganges.

### Skupper Version:
Testing has been done with RHAI a pre-release: Skupper v1.0.0 available at: https://skupper.io/install/index.html

## Overview of thie Git Repo

### /demo

### /tools
This directory tree contains scripts to set up the database back end.

### /yaml

## Environment Configuration

## Demo setup instructions and narrative
