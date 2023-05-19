FROM postgres

ENV POSTGRES_USER=demo
ENV POSTGRES_PASSWORD=demopass
ENV POSTGRES_DB=demo-db

ADD data.sql /docker-entrypoint-initdb.d/

