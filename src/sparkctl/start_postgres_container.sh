#!/bin/bash
pg_data_dir=$1
pg_run_dir=$2
pg_password=$3

# TODO: Make these configurable.
lustre_bind_mounts=" -B /nopt:/nopt \
    -B /projects:/projects \
    -B /scratch:/scratch \
    -B /datasets:/datasets \
    -B /kfs2:/kfs2 \
    -B /kfs3:/kfs3"

# TODO: Make docker vs apptainer configurable.

module load apptainer
mkdir -p ${pg_data_dir} ${pg_run_dir}
apptainer instance start \
    --env POSTGRES_PASSWORD=${pg_password} \
    ${lustre_bind_mounts} \
    -B ${pg_data_dir}:/var/lib/postgresql/data \
    -B ${pg_run_dir}:/var/run/postgresql \
    docker://postgres \
    pg-server
