#! /bin/bash

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License
#

# Note: Run this script directly if you do not want to use virtualenvwrapper

ADMIN_EMAIL=admin@demo.net
ADMIN_PWD=password
PGADMIN_PORT=8089
PGSQL_USER=demo
PGSQL_PASSWORD=demopass
PGSQL_DB=demo-db

# Check that one of Podman or Docker is installed.
echo "Checking for container runtime..."
runtime=$(which podman)
inst_status=$?
if [ $inst_status -eq 0 ]; then
   echo "Podman is installed"
   CONTAINER_RUNTIME="podman"
else
  runtime=$(which docker)
  inst_status=$?
  if [ $inst_status -eq 0 ]; then
    echo "Docker is installed"
    CONTAINER_RUNTIME="docker"
   else
      echo "ERROR: No container runtime found."
      exit
   fi
fi

# Install the python sql library so dbsetup can run
echo "Installing required python libraries..."
pip3 install psycopg2-binary

echo "Starting postgresql database"
$CONTAINER_RUNTIME run -d --rm --name nearest-prime-db -e POSTGRESQL_USER=$PGSQL_USER -e POSTGRESQL_PASSWORD=$PGSQL_PASSWORD -e POSTGRESQL_DATABASE=$PGSQL_DB -p 5432:5432 registry.redhat.io/rhel8/postgresql-13:1-56.1654147925

# TODO: Find out why running pgadmin4 does not always loop back to access the database.
# This is an environmental bug because it woks in some networks.
#echo "Starting pgadmin4"
#$CONTAINER_RUNTIME run -d --rm --name pgadmin4 -p $PGADMIN_PORT:80 -e PGADMIN_DEFAULT_PASSWORD=$ADMIN_PWD -e PGADMIN_DEFAULT_EMAIL=$ADMIN_EMAIL docker.io/dpage/pgadmin4:6.11

echo "Waiting for the database to start"
exec 2>/dev/null     # Suppress stderr while we wait
RESP=0
until [ $RESP -eq 52 ]
do
   sleep 2
   printf '.'
   curl localhost:5432
   RESP=$?
done
exec 2>/dev/tty    # Restore stderr output.

echo "Initialising database"
./dbsetup

#echo
#echo "Postgresql Admin Console access details:"
#echo "========================================"
#echo "Pgadmin URL: http://localhost:8089"
#echo "DB Admin email: " $ADMIN_EMAIL
#echo "DB Admin password: "$ADMIN_PWD
echo
echo "Database connection details:"
echo "============================"
echo "Database server url is: " $HOSTNAME
echo "Database connection port: 5432"
echo "Database database: " $PGSQL_DB
echo "Database user: " $PGSQL_USER
echo "Database password: " $PGSQL_PASSWORD
echo "To test the database has been initialised run the following query in pgadmin4:"
echo "select * from work"

