import pytest
from unittest.mock import patch
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_process_repository_success(mock_settings):
    with patch('app.services.github_service.GitHubService.download_github_repo') as mock_download, \
            patch('app.services.file_service.FileService.merge_repository_files') as mock_merge:
        mock_download.return_value = ["test.py"]
        mock_merge.return_value = "merged_file.md"

        from app.services.repository_service import RepositoryService
        result = await RepositoryService.process_repository("https://github.com/test/repo")

        assert "merged_filepath" in result
        assert "found_files" in result
        assert result["found_files"] == ["test.py"]


@pytest.mark.asyncio
async def test_process_repository_no_files(mock_settings):
    with patch('app.services.github_service.GitHubService.download_github_repo') as mock_download:
        mock_download.side_effect = HTTPException(status_code=404, detail="No suitable files found")

        from app.services.repository_service import RepositoryService
        with pytest.raises(HTTPException) as exc:
            await RepositoryService.process_repository("https://github.com/test/repo")
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_process_repository_with_error(mock_settings):
    with patch('app.services.github_service.GitHubService.download_github_repo') as mock_download:
        mock_download.side_effect = HTTPException(status_code=500, detail="Test error")

        from app.services.repository_service import RepositoryService
        with pytest.raises(HTTPException) as exc:
            await RepositoryService.process_repository("https://github.com/test/repo")
        assert exc.value.status_code == 500
