import os

import chardet


class FileService:
    @staticmethod
    def merge_repository_files(repo_folder: str, output_file: str):
        skip_extensions = {
            ".exe",
            ".zip",
            ".rar",
            ".7z",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
            ".pdf",
            ".bin",
            ".pyc",
            ".so",
            ".dll",
            ".a",
            ".lib",
        }

        def detect_and_read_file(file_path: str) -> str:
            with open(file_path, "rb") as file:
                raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result["encoding"] or "utf-8"
            try:
                content = raw_data.decode(encoding)
                return content
            except UnicodeDecodeError:
                return raw_data.decode("utf-8", errors="ignore")

        with open(output_file, "w", encoding="utf-8") as outfile:
            for root, _, files in os.walk(repo_folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, repo_folder)

                    if any(file.lower().endswith(ext) for ext in skip_extensions):
                        continue
                    if os.path.getsize(full_path) > 1024 * 1024:
                        continue

                    outfile.write(f"# File: {relative_path}\n\n")
                    file_content = detect_and_read_file(full_path)
                    outfile.write(file_content + "\n\n")

        return output_file
