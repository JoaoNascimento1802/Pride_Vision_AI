# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import time

import httpx
import jwt

from app.config import settings
from app.models.enums import GateDecision

from .base import CIPipelineProvider


class GitHubPipelineProvider(CIPipelineProvider):
    def __init__(self) -> None:
        self.api_url = settings.GITHUB_API_URL.rstrip("/")
        self.app_id = settings.GITHUB_APP_ID
        self.installation_id = settings.GITHUB_INSTALLATION_ID
        self.private_key = settings.GITHUB_PRIVATE_KEY

        self.client = httpx.Client(timeout=10.0)

    def _get_app_jwt(self) -> str:
        if not self.app_id or not self.private_key:
            raise ValueError(
                "Configuração do GitHub App incompleta (App ID ou Private Key ausentes)."
            )

        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + (10 * 60), "iss": self.app_id}
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def _get_installation_token(self) -> str:
        if not self.installation_id:
            raise ValueError("GITHUB_INSTALLATION_ID não configurado.")

        app_jwt = self._get_app_jwt()

        url = f"{self.api_url}/app/installations/{self.installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        response = self.client.post(url, headers=headers)
        response.raise_for_status()

        return str(response.json()["token"])

    def _get_headers(self) -> dict[str, str]:
        token = self._get_installation_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def publish_status(
        self,
        repository: str,
        commit_sha: str,
        decision: GateDecision,
        description: str,
        target_url: str | None = None,
    ) -> None:
        if not repository or not commit_sha:
            return

        headers = self._get_headers()
        url = f"{self.api_url}/repos/{repository}/statuses/{commit_sha}"

        state_map = {
            GateDecision.PASS: "success",
            GateDecision.WARN: "success",  # Mapeamento: warn não deve quebrar o status check nativo, usa "success"
            GateDecision.BLOCK: "failure",
        }

        # O GitHub tem um limite de 140 caracteres na descrição do status
        truncated_description = description[:140]

        payload = {
            "state": state_map.get(decision, "error"),
            "description": truncated_description,
            "context": "pride-vision/security-gate",
        }
        if target_url:
            payload["target_url"] = target_url

        try:
            self.client.post(url, headers=headers, json=payload).raise_for_status()
        except Exception:
            # Em um cenário real usaríamos logger, mas não podemos deixar quebrar o pipeline
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

        headers = self._get_headers()

        # Para ser idempotente, procuramos um comentário prévio do PRIDE
        marker = "<!-- PRIDE_SECURITY_GATE -->"
        body = f"{marker}\n\n{summary}"
        if target_url:
            body += f"\n\n[Ver detalhes no PRIDE Vision AI]({target_url})"

        url_comments = f"{self.api_url}/repos/{repository}/issues/{pr_number}/comments"

        try:
            # Tenta listar os comentários para atualizar se já existir
            resp = self.client.get(url_comments, headers=headers)
            if resp.status_code == 200:
                comments = resp.json()
                for comment in comments:
                    if marker in str(comment.get("body", "")):
                        comment_id = comment["id"]
                        url_update = (
                            f"{self.api_url}/repos/{repository}/issues/comments/{comment_id}"
                        )
                        self.client.patch(
                            url_update, headers=headers, json={"body": body}
                        ).raise_for_status()
                        return

            # Se não achou (ou falhou ao listar), cria um novo
            self.client.post(url_comments, headers=headers, json={"body": body}).raise_for_status()
        except Exception:
            pass
