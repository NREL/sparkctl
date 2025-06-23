import os
from pathlib import Path
from socket import gethostname
from typing import Any

from sparkctl.compute_interface import ComputeInterface
from sparkctl.run_command import check_run_command


class SlurmCompute(ComputeInterface):
    """Provides interface to Slurm."""

    def get_node_memory_overhead_gb(
        self, driver_memory_gb: int, node_memory_overhead_gb: int
    ) -> int:
        if self.is_heterogeneous_slurm_job():
            return node_memory_overhead_gb

        return driver_memory_gb + self._config.runtime.node_memory_overhead_gb

    def get_num_workers(self) -> int:
        master_node = gethostname()
        num_workers = 0
        for node_name in self.get_node_names():
            if not self.is_heterogeneous_slurm_job() and node_name == master_node:
                num_workers += 1

        return num_workers

    def get_node_names(self) -> list[str]:
        return get_node_names(os.environ["SLURM_JOB_ID"])

    def get_worker_node_names(self) -> list[str]:
        node_names = self.get_node_names()
        if self.is_heterogeneous_slurm_job():
            return [x for x in node_names if x != gethostname()]
        return node_names

    def get_scratch_dir(self) -> Path:
        return Path(os.environ["TMPDIR"])

    def get_worker_memory_gb(self) -> int:
        # Spark documentation recommends only using 75% of system memory,
        # leaving the rest for the OS and buffer cache.
        # https://spark.apache.org/docs/latest/hardware-provisioning.html#memory
        het_memory_group1 = os.getenv("SLURM_MEM_PER_NODE_HET_GROUP_1")
        if het_memory_group1 is not None:
            memory_gb = int(het_memory_group1) / 1024 * 3 / 4
        else:
            memory_gb = int(os.environ["SLURM_MEM_PER_NODE"]) / 1024 * 3 / 4

        return int(memory_gb)

    def get_worker_num_cpus(self) -> int:
        het_cpus = os.getenv("SLURM_JOB_CPUS_PER_NODE_HET_GROUP_1")
        if het_cpus is not None:
            num_cpus = het_cpus.split("(")[1]
        else:
            num_cpus = os.environ["SLURM_CPUS_ON_NODE"]

        return int(num_cpus)

    def is_heterogeneous_slurm_job(self) -> bool:
        return "SLURM_HET_SIZE" in os.environ

    def is_worker_node(self, node_name: str) -> bool:
        return node_name == os.getenv("SLURM_NODELIST_HET_GROUP_0", "")

    def run_checks(self) -> None:
        if "SLURM_MEM_PER_NODE" not in os.environ:
            msg = (
                "The SLURM_MEM_PER_NODE environment variable is not set. "
                "Please submit the Slurm job with --mem, such as --mem=240000, or set the variable."
            )
            raise ValueError(msg)

        if self.is_heterogeneous_slurm_job():
            het_size = int(os.getenv("SLURM_HET_SIZE", "0"))
            if het_size > 2:
                msg = f"A heterogeneous job can only have two groups: {het_size}"
                raise ValueError(msg)

            het_group_0 = int(os.getenv("SLURM_JOB_NUM_NODES_HET_GROUP_0", "0"))
            if het_group_0 != 1:
                msg = f"SLURM_JOBID_HET_GROUP_0 can only have one node: {het_group_0}"
                raise ValueError(msg)


def get_node_names(job_id: str) -> list[str]:
    # The squeue command will produce multiple lines if the job is heterogeneous.
    job_id = os.environ["SLURM_JOB_ID"]
    output: dict[str, Any] = {}
    check_run_command(f'squeue -j {job_id} --format="%5D %1000N" -h', output=output)
    hosts = output["stdout"].split()[1]  # TODO
    output.clear()
    check_run_command(f"scontrol show hostnames {hosts}", output=output)
    return output["stdout"].split()
