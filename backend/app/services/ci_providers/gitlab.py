# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import httpx

from app.config import settings
from app.models.enums import GateDecision

from .base import CIPipelineProvider


class GitLabPipelineProvider(CIPipelineProvider):
    def __init__(self) -> None:
        self.base_url = settings.GITLAB_BASE_URL.rstrip("/")
        self.api_url = f"{self.base_url}/api/v4"
        self.token = settings.GITLAB_TOKEN
        self.client = httpx.Client(timeout=10.0)

    def _get_headers(self) -> dict[str, str]:
        if not self.token:
            raise ValueError("Configuração do GitLab incompleta (Token ausente).")
        return {"PRIVATE-TOKEN": self.token, "Content-Type": "application/json"}

    def publish_status(
        self,
        repository: str,
        commit_sha: str,
        decision: GateDecision,
        description: str,
        target_url: str | None = None,
    ) -> None:
        # repository aqui seria o project_id, encodado
        if not repository or not commit_sha:
            return

        project_id = repository.replace("/", "%2F")
        headers = self._get_headers()
        url = f"{self.api_url}/projects/{project_id}/statuses/{commit_sha}"

        state_map = {
            GateDecision.PASS: "success",
            GateDecision.WARN: "success",  # GitLab statuses: success, failed, canceled
            GateDecision.BLOCK: "failed",
        }

        payload = {
            "state": state_map.get(decision, "failed"),
            "description": description[:140],
            "name": "pride-vision/security-gate",
        }
        if target_url:
            payload["target_url"] = target_url

        try:
            self.client.post(url, headers=headers, json=payload).raise_for_status()
        except Exception:
            pass

    def publish_pr_feedback(
        self,
        repository: str,
        pr_number: int,
        decision: GateDecision,
        summary: str,
        target_url: str | None = None,
    ) -> None:
        if not repository or not pr_number:
            return

        project_id = repository.replace("/", "%2F")
        headers = self._get_headers()

        marker = "<!-- PRIDE_SECURITY_GATE -->"
        body = f"{marker}\n\n{summary}"
        if target_url:
            body += f"\n\n[Ver detalhes no PRIDE Vision AI]({target_url})"

        url_notes = f"{self.api_url}/projects/{project_id}/merge_requests/{pr_number}/notes"

        try:
            resp = self.client.get(url_notes, headers=headers)
            if resp.status_code == 200:
                notes = resp.json()
                for note in notes:
                    if marker in str(note.get("body", "")):
                        note_id = note["id"]
                        url_update = f"{url_notes}/{note_id}"
                        self.client.put(
                            url_update, headers=headers, json={"body": body}
                        ).raise_for_status()
                        return

            self.client.post(url_notes, headers=headers, json={"body": body}).raise_for_status()
        except Exception:
            pass
