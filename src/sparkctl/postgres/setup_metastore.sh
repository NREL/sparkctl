#!/bin/bash
pg_exists=$1
pg_password=$2
module load apptainer

echo "the value of pg_exists is $pg_exists"
if [ "${pg_exists}" != "true" ]; then
    echo "pg_exists is not true, call initdb"
    apptainer exec instance://pg-server initdb
fi
set -e
apptainer exec instance://pg-server \
    pg_ctl \
        -D /var/lib/postgresql/data \
        -l pg_logfile \
        start
if [ "${pg_exists}" != "true" ]; then
    echo "pg_exists is not true, call createdb"
    apptainer exec instance://pg-server createdb hive_metastore
    apptainer exec instance://pg-server \
        psql \
            -c "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD '${pg_password}'" \
            hive_metastore
fi
