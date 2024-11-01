import pytest
from unittest.mock import patch, Mock

from app.services.github_service import GitHubService


def test_get_repo_details():
    url = "https://github.com/user/repo"
    result = GitHubService.get_repo_details(url)
    assert result["owner"] == "user"
    assert result["repo"] == "repo"


@pytest.mark.asyncio
async def test_github_download_success(tmp_path):
    async def mock_get(*args, **kwargs):
        response = Mock()
        if 'contents' in args[0]:
            response.json.return_value = [{
                "type": "file",
                "name": "test.py",
                "path": "test.py",
                "download_url": "http://test.com"
            }]
        else:
            response.content = b"test content"
        return response

    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = Mock()
        mock_instance.get = mock_get
        mock_client.return_value.__aenter__.return_value = mock_instance

        result = await GitHubService.download_github_repo(
            "https://github.com/test/repo",
            "test-token",
            str(tmp_path)
        )
        assert isinstance(result, list)
