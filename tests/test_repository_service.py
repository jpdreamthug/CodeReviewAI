import pytest
from unittest.mock import patch
from fastapi import HTTPException
from app.services.repository_service import RepositoryService


@pytest.mark.asyncio
async def test_process_repository_success():
    with patch('app.services.github_service.GitHubService.download_github_repo') as mock_download, \
            patch('app.services.file_service.FileService.merge_repository_files') as mock_merge:
        mock_download.return_value = ["conftest.py"]
        mock_merge.return_value = "merged_file.md"

        result = await RepositoryService.process_repository("https://github.com/test/repo")
        assert "merged_filepath" in result
        assert "found_files" in result
        assert result["found_files"] == ["conftest.py"]


@pytest.mark.asyncio
async def test_process_repository_no_files():
    with patch('app.services.github_service.GitHubService.download_github_repo') as mock_download:
        mock_download.return_value = []

        with pytest.raises(HTTPException) as exc:
            await RepositoryService.process_repository("https://github.com/test/repo")
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_clean_temp_repos(tmp_path):
    test_dir = tmp_path / "test_repo"
    test_dir.mkdir()
    (test_dir / "conftest.py").write_text("test")

    RepositoryService.clean_temp_repos(str(test_dir))
    assert not test_dir.exists()


@pytest.mark.asyncio
async def test_process_repository_with_error():
    with patch('app.services.github_service.GitHubService.download_github_repo') as mock_download:
        mock_download.side_effect = Exception("Test error")

        with pytest.raises(HTTPException) as exc:
            await RepositoryService.process_repository("https://github.com/test/repo")
        assert exc.value.status_code == 500
