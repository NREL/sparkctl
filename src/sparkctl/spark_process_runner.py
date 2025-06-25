import os
import subprocess
from loguru import logger
from typing import Any

from sparkctl.models import SparkConfig
from sparkctl.run_command import check_run_command, run_command


class SparkProcessRunner:
    """Runs Spark processes."""

    def __init__(self, config: SparkConfig, url: str) -> None:
        self._spark_path = config.binaries.spark_path
        self._java_path = config.binaries.java_path
        self._conf_dir = config.directories.get_spark_conf_dir()
        self._config = config
        self._url = url

    def start_master_process(self) -> None:
        """Start the Spark master process."""
        self._check_run_command(self._start_master_cmd())

    def stop_master_process(self) -> int:
        """Stop the Spark master process."""
        return self._run_command(self._stop_master_cmd())

    def start_connect_server(self) -> None:
        """Start the Spark connect server."""
        self._check_run_command(self._start_connect_server_cmd())

    def stop_connect_server(self) -> int:
        """Stop the Spark connect server."""
        return self._run_command(self._stop_connect_server_cmd())

    def start_history_server(self) -> None:
        """Start the Spark history_server."""
        self._check_run_command(self._start_history_server_cmd())

    def stop_history_server(self) -> int:
        """Stop the Spark history_server."""
        return self._run_command(self._stop_history_server_cmd())

    def start_thrift_server(self) -> None:
        """Start the Apache Thrift server."""
        script = self._start_thrift_server_cmd()
        self._check_run_command(f"{script} --master {self._url}")

    def stop_thrift_server(self) -> int:
        """Stop the Apache Thrift server."""
        return self._run_command(self._stop_thrift_server_cmd())

    def start_worker_process(self, memory_gb: int | None = None) -> None:
        """Start one Spark worker process."""
        self._start_workers(self._start_worker_cmd(), memory_gb)

    def stop_worker_process(self) -> int:
        """Stop the Spark workers."""
        return self._run_command(self._stop_worker_cmd())

    def start_worker_processes(self, workers: list[str], memory_gb: float | None = None) -> None:
        """Start the Spark worker processes."""
        # Calling Spark's start-workers.sh doesn't work because there is no way to forward
        # SPARK_CONF_DIR through ssh in their scripts.
        start_script = self._sbin_cmd("start-worker.sh")
        content = f"""#!/bin/bash
export SPARK_CONF_DIR={self._conf_dir}
{start_script} {self._url} -m {memory_gb}g
"""
        tmp_script = self._conf_dir / "tmp_start_worker.sh"
        tmp_script.write_text(content, encoding="utf-8")
        try:
            for worker in workers:
                cmd = f"ssh {worker} bash {tmp_script}"
                subprocess.run(cmd, check=True, shell=True)
        finally:
            tmp_script.unlink()

    def stop_worker_processes(self, workers: list[str]) -> int:
        """Stop the Spark workers."""
        stop_script = self._stop_worker_cmd()
        content = f"""#!/bin/bash
export SPARK_CONF_DIR={self._conf_dir}
{stop_script}
"""
        tmp_script = self._conf_dir / "tmp_stop_worker.sh"
        tmp_script.write_text(content, encoding="utf-8")
        ret = 0
        for worker in workers:
            cmd = f"ssh {worker} bash {tmp_script}"
            pipe = subprocess.run(cmd, shell=True)
            if pipe.returncode != 0:
                logger.error("Failed to stop worker on {}: {}", worker, pipe.returncode)
                ret = pipe.returncode
        tmp_script.unlink()
        return ret

    def _start_workers(self, script: str, memory_gb: float | None) -> None:
        cmd = f"{script} {self._url}"
        if memory_gb is not None:
            cmd += f" -m {memory_gb}G"
        self._check_run_command(cmd)

    def _start_master_cmd(self) -> str:
        return self._sbin_cmd("start-master.sh")

    def _stop_master_cmd(self) -> str:
        return self._sbin_cmd("stop-master.sh")

    def _start_connect_server_cmd(self) -> str:
        return self._sbin_cmd("start-connect-server.sh")

    def _stop_connect_server_cmd(self) -> str:
        return self._sbin_cmd("stop-connect-server.sh")

    def _start_history_server_cmd(self) -> str:
        return self._sbin_cmd("start-history-server.sh")

    def _stop_history_server_cmd(self) -> str:
        return self._sbin_cmd("stop-history-server.sh")

    def _start_thrift_server_cmd(self) -> str:
        return self._sbin_cmd("start-thriftserver.sh")

    def _stop_thrift_server_cmd(self) -> str:
        return self._sbin_cmd("stop-thriftserver.sh")

    def _start_worker_cmd(self) -> str:
        return self._sbin_cmd("start-worker.sh")

    def _stop_worker_cmd(self) -> str:
        return self._sbin_cmd("stop-worker.sh")

    def _start_workers_cmd(self) -> str:
        return self._sbin_cmd("start-workers.sh")

    def _stop_workers_cmd(self) -> str:
        return self._sbin_cmd("stop-workers.sh")

    def _sbin_cmd(self, name: str) -> str:
        return str(self._spark_path / "sbin" / name)

    def _check_run_command(self, cmd: str) -> None:
        check_run_command(cmd, env=self._get_env())

    def _run_command(self, cmd: str) -> int:
        return run_command(cmd, env=self._get_env())

    def _get_env(self) -> dict[str, Any]:
        env = {k: v for k, v in os.environ.items()}
        env["SPARK_CONF_DIR"] = str(self._conf_dir)
        env["JAVA_HOME"] = str(self._java_path)
        return env
