import os
import httpx
import logging
from typing import Dict, List
from fastapi import HTTPException


class GitHubService:
    logger = logging.getLogger("github_service")

    ALLOWED_EXTENSIONS: set[str] = {
        ".py",
        ".js",
        ".jsx",
        ".html",
        ".css",
        ".ts",
        ".tsx",
    }

    @staticmethod
    def get_repo_details(github_url: str) -> Dict[str, str]:
        parts = github_url.rstrip("/").split("/")
        return {
            "owner": parts[-2],
            "repo": parts[-1],
        }

    @staticmethod
    async def download_github_repo(
        github_url: str,
        token: str,
        output_directory: str,
    ) -> List[str]:
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

                    if response.status_code == 404:
                        raise HTTPException(
                            status_code=404, detail="Repository not found"
                        )
                    if response.status_code == 401:
                        raise HTTPException(
                            status_code=401, detail="Invalid GitHub token"
                        )
                    if response.status_code == 403:
                        raise HTTPException(
                            status_code=403, detail="GitHub API rate limit exceeded"
                        )

                    response.raise_for_status()
                    content = response.json()

                    for item in content:
                        local_path = os.path.join(output_directory, item["path"])

                        if item["type"] == "dir":
                            os.makedirs(local_path, exist_ok=True)
                            await download_files(item["path"])

                        elif item["type"] == "file":
                            if (
                                os.path.splitext(item["name"])[1]
                                in GitHubService.ALLOWED_EXTENSIONS
                            ):
                                file_response = await client.get(
                                    item["download_url"], headers=headers
                                )
                                file_response.raise_for_status()

                                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                                with open(local_path, "wb") as file:
                                    file.write(file_response.content)

                                downloaded_files.append(item["path"])
                                GitHubService.logger.info(
                                    f"File downloaded: {item['path']}"
                                )

            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=str(e))

        os.makedirs(output_directory, exist_ok=True)
        await download_files()

        if not downloaded_files:
            raise HTTPException(status_code=404, detail="No suitable files found")

        return downloaded_files
