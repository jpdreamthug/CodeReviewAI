import os
import shutil
import uuid
import logging
from fastapi import HTTPException
from app.core.config import settings
from app.services.file_service import FileService
from app.services.github_service import GitHubService


class RepositoryService:
    logger = logging.getLogger("repository_service")

    @staticmethod
    async def process_repository(github_url: str) -> dict:
        repository_id = str(uuid.uuid4())
        repo_folder = f"../temp_repos/{repository_id}"
        merged_file = f"../temp_repos/{repository_id}_merged.md"

        try:
            os.makedirs(os.path.dirname(merged_file), exist_ok=True)

            found_files = await GitHubService.download_github_repo(
                github_url=str(github_url),
                token=settings.GITHUB_TOKEN,
                output_directory=repo_folder,
            )

            merged_filepath = FileService.merge_repository_files(
                repo_folder=repo_folder, output_file=merged_file
            )

            return {"merged_filepath": merged_filepath, "found_files": found_files}

        finally:
            if os.path.exists(repo_folder):
                shutil.rmtree(repo_folder, ignore_errors=True)
