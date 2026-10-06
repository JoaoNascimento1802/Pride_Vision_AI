# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import abc

from app.models.enums import GateDecision


class CIPipelineProvider(abc.ABC):
    """
    Abstração para comunicação com plataformas de CI/CD (GitHub, GitLab, etc).
    """

    @abc.abstractmethod
    def publish_status(
        self,
        repository: str,
        commit_sha: str,
        decision: GateDecision,
        description: str,
        target_url: str | None = None,
    ) -> None:
        """
        Publica um status ou Check Run no commit correspondente.
        """
        pass

    @abc.abstractmethod
    def publish_pr_feedback(
        self,
        repository: str,
        pr_number: int,
        decision: GateDecision,
        summary: str,
        target_url: str | None = None,
    ) -> None:
        """
        Publica ou atualiza um comentário/feedback no Pull Request/Merge Request.
        Deve ser idempotente.
        """
        pass
