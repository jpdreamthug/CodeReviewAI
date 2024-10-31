import os
import requests


class GitHubService:

    @staticmethod
    def get_repo_details(github_url: str) -> dict:
        parts = github_url.strip("/").split("/")
        return {
            "owner": parts[-2],
            "repo": parts[-1],
        }

    @staticmethod
    def download_github_repo(
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

        def download_files(path="") -> None:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            content = response.json()
            for item in content:
                local_path = os.path.join(output_directory, item["path"])
                if item["type"] == "dir":
                    os.makedirs(local_path, exist_ok=True)
                    download_files(item["path"])
                elif item["type"] == "file":
                    downloaded_files.append(item["path"])
                    file_response = requests.get(item["download_url"], headers=headers)
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    with open(local_path, "wb") as file:
                        file.write(file_response.content)

        os.makedirs(output_directory, exist_ok=True)
        download_files()
        return downloaded_files
