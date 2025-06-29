# sparkctl
This package extends the Apache Spark launcher scripts to support ephemeral clusters in non-cloud
environments where infrastructure is not already present, such as on HPC compute nodes.

Refer to the [user documentation](https://pages.github.nrel.gov/dthom/sparkctl/) for a description
of features and usage instructions.

## Project Status
The package is actively maintained and used at the National Renewable Energy Laboratory (NREL).
The software is primarily geared toward HPCs that use Slurm.

It would be straightforward to extend the functionality to support (1) other HPC resource managers
or (2) a generic list of servers. Please submit an issue or idea or discussion if you have interest
in this package but need that support.

Contributions are welcome.

## License
sparkctl is released under a BSD 3-Clause [license](https://github.nrel.gov/dthom/LICENSE).
