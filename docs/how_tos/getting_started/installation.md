# Installation

1. Create a Python 3.11+ virtual environment. This example uses the `venv` module in the standard
   library to create a virtual environment in your home directory.

   You may prefer `conda` or `mamba`.

   If you are running on an HPC, you may need to `module load python` first.

   ```console
   $ python -m venv ~/python-envs/sparkctl
   ```

2. Activate the virtual environment.

   ```console
   $ source ~/python-envs/sparkctl/bin/activate
   ```

   Whenever you are done using sparkctl, you can deactivate the environment by running `deactivate`.

3. Install the Python package `sparkctl`.

   ```console
   $ pip install sparkctl
   ```

4. Optional, install from the main branch (or substitute another branch or tag).

   ```console
   $ pip install git+https://github.nrel.gov/dthom/sparkctl.git@main
   ```

5. Optional, install `pyspark` or `pyspark-client` if you will be running a pyspark-based Python
   application.

6. Create a one-time sparkctl default configuration file. The parameters will vary based on your
   environment.

   ```bash
   $ sparkctl default-config \
       /datasets/images/apache_spark/spark-4.0.0-bin-hadoop3 \
       /datasets/images/apache_spark/jdk-21.0.7 \
       --compute-environment slurm
   ```
   ```bash
   Wrote sparkctl settings to /Users/dthom/.sparkctl.toml
   ```
   Refer to `sparkctl default-config --help` for additional options.
   
   The paths to the Spark binaries will likely not change often. This file will also seed the default
   values for your `sparkctl configure` commands, and so you may want to manually edit those settings.
