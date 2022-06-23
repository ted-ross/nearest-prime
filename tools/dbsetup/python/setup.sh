#! /bin/bash

# Select the Python virtual environment. Assumes that virtualenv and virtualenvwrapper is installed and nearest-prime workspace has been created
workon nearest-prime

# If you want to run Postresql on OpenShift Local then you can swap podman out for the openshift commands. It assumes you have created the project already
#oc new-app -e POSTGRESQL_USER=demo -e POSTGRESQL_PASSWORD=demopass -e POSTGRESQL_DATABASE=demo-db postgresql
#oc expose deployment/postgresql --type=LoadBalancer --name=postgresql-ingress
podman run -d --name postgresql_database -e POSTGRESQL_USER=demo -e POSTGRESQL_PASSWORD=demopass -e POSTGRESQL_DATABASE=demo-db -p 5432:5432 registry.redhat.io/rhel8/postgresql-13:1-56.1654147925

export DDW_HOST=localhost     # Change this to $(crc ip) if you want to run Postresql on minishift
export DDW_PORT=5432          # Change this to the node port is you want to run on minishift

echo "Script to set up environment variables for dbsetup.py."
echo "This script replies on having a node port defined on the Postgresql service"
echo "DDW_HOST = $DDW_HOST"
echo "DDW_PORT = $DDW_PORT"

# Install the python sql library
pip3 install psycopg2-binary

# Initialise the demo database
./dbsetup
