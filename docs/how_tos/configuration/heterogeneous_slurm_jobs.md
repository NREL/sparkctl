(heterogeneous-slurm-jobs)=

# Heterogeneous Slurm jobs
The scripts in this package are well-suited for an environment where the
Spark cluster manager, driver, and user application run on a shared node with a limited number of
CPUs, and the workers run on exclusive nodes with uniform resources. Refer to this
[diagram](https://spark.apache.org/docs/latest/cluster-overview.html) to see an illustration
of the Spark cluster components.

This can be achieved with
[Slurm heterogeneous jobs](https://slurm.schedmd.com/heterogeneous_jobs.html).

Here is one possible configuration:
- Spark driver memory = 10 GB
- Spark master memory + overhead for OS and Slurm = 20 GB
- CPUs for Spark master, driver, user application, and overhead for OS and Slurm = 4

Allocate one compute node from the shared partition and then four from the regular partition.

```{eval-rst}
.. note:: The shared partition must be first and must have only one compute node.
   That is where your application will run.
```

## Interactive job
```console
$ salloc --account=<your-account> -t 01:00:00 -n4 --mem=30G --partition=shared : \
    -N2 --partition=debug --mem=240G
```

## Batch job
Here is the format of sbatch script:
```bash
#!/bin/bash
#SBATCH --account=<my-account>
#SBATCH --job-name=my-job
#SBATCH --time=4:00:00
#SBATCH --output=output_%j.o
#SBATCH --error=output_%j.e
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --mem=30G
#SBATCH --ntasks=4
#SBATCH hetjob
#SBATCH --nodes=2
#SBATCH --mem=240G
```

You will need to adjust the CPU and memory parameters based on what you will pass to
`sparkctl configure`.

Then proceed with the rest of the instructions.
