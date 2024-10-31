import os
import shutil
import uuid

from app.core.config import settings
from app.services.file_service import FileService
from app.services.github_service import GitHubService


class RepositoryService:

    @staticmethod
    async def process_repository(github_url: str) -> dict:
        repo_folder = f"../temp_repos/{uuid.uuid4()}"
        merged_file = f"../temp_repos/{uuid.uuid4()}_merged.md"

        os.makedirs(os.path.dirname(merged_file), exist_ok=True)

        found_files = GitHubService.download_github_repo(
            github_url=str(github_url),
            token=settings.GITHUB_TOKEN,
            output_directory=repo_folder
        )

        merged_filepath = FileService.merge_repository_files(
            repo_folder=repo_folder,
            output_file=merged_file
        )

        RepositoryService.clean_temp_repos(repo_folder=repo_folder)

        return {
            "merged_filepath": merged_filepath,
            "found_files": found_files
        }

    @staticmethod
    def clean_temp_repos(repo_folder: str):
        shutil.rmtree(repo_folder, ignore_errors=True)
