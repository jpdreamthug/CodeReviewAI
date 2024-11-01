import os
import logging
import chardet


class FileService:
    logger = logging.getLogger("file_service")

    @staticmethod
    def detect_and_read_file(file_path: str) -> str:
        with open(file_path, "rb") as file:
            raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result["encoding"] or "utf-8"
        return raw_data.decode(encoding, errors="ignore")

    @staticmethod
    def merge_repository_files(repo_folder: str, output_file: str) -> str:
        with open(output_file, "w", encoding="utf-8") as outfile:
            for root, _, files in os.walk(repo_folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, repo_folder)

                    if os.path.getsize(full_path) > 1024 * 1024:
                        continue

                    file_content = FileService.detect_and_read_file(full_path)
                    outfile.write(f"# File: {relative_path}\n\n")
                    outfile.write(file_content + "\n\n")

        return output_file
