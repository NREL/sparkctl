from sparkctl.compute_interface import ComputeInterface
from sparkctl.models import ComputeEnvironment, SparkConfig
from sparkctl.local_compute import LocalCompute
from sparkctl.slurm_compute import SlurmCompute


def make_compute_interface(config: SparkConfig) -> ComputeInterface:
    """Return a compute interface appropriate for teh current environment."""
    match config.compute.environment:
        case ComputeEnvironment.SLURM:
            return SlurmCompute(config)
        case ComputeEnvironment.LOCAL:
            return LocalCompute(config)
        case _:
            msg = f"{config.environment=} is not supported"
            raise NotImplementedError(msg)
