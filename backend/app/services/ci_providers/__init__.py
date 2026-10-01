from .base import CIPipelineProvider
from .github import GitHubPipelineProvider
from .gitlab import GitLabPipelineProvider


def get_ci_provider(provider_name: str) -> CIPipelineProvider | None:
    if provider_name.lower() == "github":
        return GitHubPipelineProvider()
    elif provider_name.lower() == "gitlab":
        return GitLabPipelineProvider()
    return None
