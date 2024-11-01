import logging
import os
from typing import Dict, List, Set

import httpx
from fastapi import HTTPException


class GitHubService:
    logger = logging.getLogger('github_service')

    ALLOWED_EXTENSIONS: Set[str] = {
        ".py", ".js", ".jsx", ".html", ".css", ".ts", ".tsx"
    }

    @staticmethod
    def get_repo_details(github_url: str) -> Dict[str, str]:
        try:
            parts = github_url.rstrip('/').split('/')
            return {
                "owner": parts[-2],
                "repo": parts[-1],
            }
        except Exception as e:
            GitHubService.logger.error(f"Error parsing GitHub URL: {e}")
            raise HTTPException(status_code=400, detail="Invalid GitHub URL format")

    @staticmethod
    async def download_github_repo(
            github_url: str,
            token: str,
            output_directory: str,
    ) -> List[str]:
        try:
            GitHubService.logger.info(f"Starting repository download: {github_url}")

            repo_details = GitHubService.get_repo_details(github_url)
            owner, repo = repo_details["owner"], repo_details["repo"]

            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            }

            downloaded_files = []

            async def download_files(path="") -> None:
                api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(api_url, headers=headers)
                        response.raise_for_status()
                        content = response.json()

                        for item in content:
                            local_path = os.path.join(output_directory, item["path"])

                            if item["type"] == "dir":
                                os.makedirs(local_path, exist_ok=True)
                                await download_files(item["path"])

                            elif item["type"] == "file":
                                file_extension = os.path.splitext(item["name"])[1]

                                if file_extension in GitHubService.ALLOWED_EXTENSIONS:
                                    try:
                                        file_response = await client.get(
                                            item["download_url"],
                                            headers=headers
                                        )
                                        file_response.raise_for_status()

                                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                                        with open(local_path, "wb") as file:
                                            file.write(file_response.content)

                                        downloaded_files.append(item["path"])
                                        GitHubService.logger.info(f"File downloaded: {item['path']}")
                                    except Exception as e:
                                        GitHubService.logger.error(f"Error downloading file {item['path']}: {e}")

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        GitHubService.logger.error("Repository not found")
                        raise HTTPException(status_code=404, detail="Repository not found")
                    elif e.response.status_code == 401:
                        GitHubService.logger.error("Invalid GitHub token")
                        raise HTTPException(status_code=401, detail="Invalid GitHub token")
                    raise HTTPException(status_code=500, detail="Error downloading files")

            os.makedirs(output_directory, exist_ok=True)
            await download_files()

            if not downloaded_files:
                GitHubService.logger.warning("No files found for download")

            return downloaded_files

        except HTTPException:
            raise
        except Exception as e:
            GitHubService.logger.error(f"Repository processing error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to download repository files"
            )
