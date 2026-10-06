# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from .base import CIPipelineProvider
from .github import GitHubPipelineProvider
from .gitlab import GitLabPipelineProvider


def get_ci_provider(provider_name: str) -> CIPipelineProvider | None:
    if provider_name.lower() == "github":
        return GitHubPipelineProvider()
    elif provider_name.lower() == "gitlab":
        return GitLabPipelineProvider()
    return None
