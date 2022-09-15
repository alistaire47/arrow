import json
import uuid
from pathlib import Path
from typing import List

from benchadapt import BenchmarkResult
from benchadapt.adapters import BenchmarkAdapter

ARROW_ROOT = Path(__file__).parent.parent.parent.resolve()
SCRIPTS_PATH = ARROW_ROOT / "ci" / "scripts"


class GoAdapter(BenchmarkAdapter):
    result_file = "bench_stats.json"
    command = ["sh", SCRIPTS_PATH / "go_bench.sh", ARROW_ROOT, "-json"]

    def __init__(self) -> None:
        super().__init__(command=self.command)

    def transform_results(self) -> List[BenchmarkResult]:
        with open(self.result_file, "r") as f:
            raw_results = json.load(f)

        parsed_results = []
        for suite in raw_results[0]["Suites"]:
            batch_id = uuid.uuid4().hex

            for benchmark in suite["Benchmarks"]:
                data = benchmark["Mem"]["MBPerSec"] * 1e6
                time = 1 / benchmark["NsPerOp"] * 1e9

                parsed = BenchmarkResult(
                    run_name=benchmark["Name"],
                    batch_id=batch_id,
                    stats={
                        "data": [data],
                        "units": "b/s",
                        "times": [time],
                        "times_unit": "i/s",
                    },
                    context={"benchmark_language": "Go"},
                )

                parsed_results.append(parsed)

        return parsed_results


if __name__ == "__main__":
    go_adapter = GoAdapter()
    go_adapter.run()
