# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from unittest.mock import patch

import pytest

from app.models.enums import GateDecision
from app.services.ci_providers.github import GitHubPipelineProvider
from app.services.ci_providers.gitlab import GitLabPipelineProvider


@pytest.fixture
def github_provider():
    with patch("app.services.ci_providers.github.settings") as mock_settings:
        mock_settings.GITHUB_API_URL = "https://api.github.com"
        mock_settings.GITHUB_APP_ID = "12345"
        mock_settings.GITHUB_INSTALLATION_ID = "67890"
        mock_settings.GITHUB_PRIVATE_KEY = "dummy-key"
        with patch("app.services.ci_providers.github.httpx.Client") as mock_client:
            yield GitHubPipelineProvider(), mock_client.return_value


@pytest.fixture
def gitlab_provider():
    with patch("app.services.ci_providers.gitlab.settings") as mock_settings:
        mock_settings.GITLAB_BASE_URL = "https://gitlab.com"
        mock_settings.GITLAB_TOKEN = "glpat-dummy"
        with patch("app.services.ci_providers.gitlab.httpx.Client") as mock_client:
            yield GitLabPipelineProvider(), mock_client.return_value


@patch("app.services.ci_providers.github.jwt.encode")
def test_github_publish_status_pass(mock_jwt, github_provider):
    mock_jwt.return_value = "dummy-jwt"
    provider, mock_client = github_provider

    # Mock installation token response
    mock_client.post.return_value.json.return_value = {"token": "ghs_dummy"}
    mock_client.post.return_value.status_code = 201

    provider.publish_status("owner/repo", "sha123", GateDecision.PASS, "Tudo certo")

    # Verifica se pegou token
    mock_client.post.assert_any_call(
        "https://api.github.com/app/installations/67890/access_tokens",
        headers={
            "Authorization": "Bearer dummy-jwt",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    # Verifica se chamou status check
    mock_client.post.assert_any_call(
        "https://api.github.com/repos/owner/repo/statuses/sha123",
        headers={
            "Authorization": "Bearer ghs_dummy",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={
            "state": "success",
            "description": "Tudo certo",
            "context": "pride-vision/security-gate",
        },
    )


@patch("app.services.ci_providers.github.jwt.encode")
def test_github_publish_pr_feedback_create(mock_jwt, github_provider):
    mock_jwt.return_value = "dummy-jwt"
    provider, mock_client = github_provider

    # Mock responses
    mock_client.post.return_value.json.return_value = {"token": "ghs_dummy"}
    mock_client.post.return_value.status_code = 201

    # Mock list comments (vazio)
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = []

    provider.publish_pr_feedback("owner/repo", 42, GateDecision.BLOCK, "Blocked")

    mock_client.post.assert_any_call(
        "https://api.github.com/repos/owner/repo/issues/42/comments",
        headers={
            "Authorization": "Bearer ghs_dummy",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"body": "<!-- PRIDE_SECURITY_GATE -->\n\nBlocked"},
    )


@patch("app.services.ci_providers.github.jwt.encode")
def test_github_publish_pr_feedback_update(mock_jwt, github_provider):
    mock_jwt.return_value = "dummy-jwt"
    provider, mock_client = github_provider

    # Mock responses
    mock_client.post.return_value.json.return_value = {"token": "ghs_dummy"}
    mock_client.post.return_value.status_code = 201

    # Mock list comments (com comentário existente)
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = [
        {"id": 999, "body": "Algum outro comentario"},
        {"id": 1000, "body": "Aqui tem <!-- PRIDE_SECURITY_GATE --> e tal"},
    ]

    provider.publish_pr_feedback("owner/repo", 42, GateDecision.WARN, "Warned")

    mock_client.patch.assert_called_once_with(
        "https://api.github.com/repos/owner/repo/issues/comments/1000",
        headers={
            "Authorization": "Bearer ghs_dummy",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"body": "<!-- PRIDE_SECURITY_GATE -->\n\nWarned"},
    )


def test_gitlab_publish_status(gitlab_provider):
    provider, mock_client = gitlab_provider

    provider.publish_status("group/repo", "sha123", GateDecision.BLOCK, "Falhou")

    mock_client.post.assert_called_once_with(
        "https://gitlab.com/api/v4/projects/group%2Frepo/statuses/sha123",
        headers={"PRIVATE-TOKEN": "glpat-dummy", "Content-Type": "application/json"},
        json={"state": "failed", "description": "Falhou", "name": "pride-vision/security-gate"},
    )


def test_gitlab_publish_pr_feedback_create(gitlab_provider):
    provider, mock_client = gitlab_provider

    # Mock list notes (vazio)
    mock_client.get.return_value.status_code = 200
    mock_client.get.return_value.json.return_value = []

    provider.publish_pr_feedback("group/repo", 10, GateDecision.PASS, "Passou")

    mock_client.post.assert_called_once_with(
        "https://gitlab.com/api/v4/projects/group%2Frepo/merge_requests/10/notes",
        headers={"PRIVATE-TOKEN": "glpat-dummy", "Content-Type": "application/json"},
        json={"body": "<!-- PRIDE_SECURITY_GATE -->\n\nPassou"},
    )
