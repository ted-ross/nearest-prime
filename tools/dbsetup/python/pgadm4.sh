#! /bin/bash

ADMIN_EMAIL=brbaker@redhat.com
ADMIN_PWD=password
PGADMIN_PORT=8089
PGSQL_USER=demo
PGSQL_PASSWORD=demopass
PGSQL_DB=demo_db

echo "Starting postgresql database"
podman run -d --rm --name nearest-prime-db -e POSTGRESQL_USER=$PGSQL_USER -e POSTGRESQL_PASSWORD=$PGSQL_PASSWORD -e POSTGRESQL_DATABASE=$PGSQL_DB -p 5432:5432 registry.redhat.io/rhel8/postgresql-13:1-56.1654147925

echo "Starting pgadmin4"
podman run -d --rm --name pgadmin4 -p $PGADMIN_PORT:80 -e PGADMIN_DEFAULT_PASSWORD=$ADMIN_PWD -e PGADMIN_DEFAULT_EMAIL=$ADMIN_EMAIL docker.io/dpage/pgadmin4:latest

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

echo
echo "Postgresql Admin Console access details:"
echo "========================================"
echo "Pgadmin URL: http://localhost:8089"
echo "DB Admin email: " $ADMIN_EMAIL
echo "DB Admin password: "$ADMIN_PWD
echo
echo "Database connection details:"
echo "============================"
echo "Database server url is: " $HOSTNAME
echo "Database connection port: 5432"
echo "Database database: " $PGSQL_DB
echo "Database user: " $PGSQL_USER
echo "Database password: " $PGSQL_PASSWORD

