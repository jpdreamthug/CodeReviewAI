import os
import httpx


class GitHubService:
    ALLOWED_EXTENSIONS: set[str] = {".py", ".js", ".jsx", ".html", ".css", ".ts", ".tsx"}

    @staticmethod
    def get_repo_details(github_url: str) -> dict:
        parts = github_url.strip("/").split("/")
        return {
            "owner": parts[-2],
            "repo": parts[-1],
        }

    @staticmethod
    async def download_github_repo(
        github_url: str,
        token: str,
        output_directory: str,
    ) -> list[str]:

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
                            if os.path.splitext(item["name"])[1] in GitHubService.ALLOWED_EXTENSIONS:
                                downloaded_files.append(item["path"])
                                try:
                                    file_response = await client.get(item["download_url"], headers=headers)
                                    file_response.raise_for_status()
                                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                                    with open(local_path, "wb") as file:
                                        file.write(file_response.content)
                                except httpx.HTTPStatusError as e:
                                    print(f"Error downloading file {item['path']}: {e}")
            except httpx.HTTPStatusError as e:
                print(f"Error fetching repository contents at {api_url}: {e}")

        os.makedirs(output_directory, exist_ok=True)
        await download_files()
        return downloaded_files
