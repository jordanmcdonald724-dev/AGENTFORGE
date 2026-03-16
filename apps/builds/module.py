from __future__ import annotations

from typing import Dict

from services.autopsy_service import AutopsyService
from services.project_genome_service import ProjectGenomeService


class BuildsApp:
    """Coordinates build execution and reporting."""

    def __init__(self, genome: ProjectGenomeService, autopsy: AutopsyService) -> None:
        self.genome = genome
        self.autopsy = autopsy

    def start_build(self, project_id: str) -> Dict[str, str]:
        summary = self.genome.compile_genome(project_id, documents=[])
        return {"project_id": project_id, "status": "started", "summary": summary}

    def finalize(self, logs: list[str]) -> Dict[str, object]:
        report = self.autopsy.analyze_run(logs)
        return {"status": "complete", "report": report}

