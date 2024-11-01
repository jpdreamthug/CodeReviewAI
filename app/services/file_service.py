import logging
import os

import chardet


class FileServiceError(Exception):
    pass


class FileService:
    logger = logging.getLogger('file_service')

    @staticmethod
    def detect_and_read_file(file_path: str) -> str:
        try:
            with open(file_path, "rb") as file:
                raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result["encoding"] or "utf-8"

            try:
                content = raw_data.decode(encoding)
                FileService.logger.debug(f"Successfully read file: {file_path}")
                return content
            except UnicodeDecodeError as e:
                FileService.logger.warning(
                    f"UnicodeDecodeError for {file_path}, falling back to utf-8 with ignore: {e}")
                return raw_data.decode("utf-8", errors="ignore")

        except Exception as e:
            FileService.logger.error(f"Error reading file {file_path}: {e}")
            raise FileServiceError(f"Failed to read file {file_path}: {str(e)}")

    @staticmethod
    def merge_repository_files(repo_folder: str, output_file: str) -> str:
        try:
            FileService.logger.info(f"Starting file merge from {repo_folder}")

            if not os.path.exists(repo_folder):
                error_msg = f"Repository folder not found: {repo_folder}"
                FileService.logger.error(error_msg)
                raise FileServiceError(error_msg)

            with open(output_file, "w", encoding="utf-8") as outfile:
                files_processed = 0
                for root, _, files in os.walk(repo_folder):
                    for file in files:
                        try:
                            full_path = os.path.join(root, file)
                            relative_path = os.path.relpath(full_path, repo_folder)

                            if os.path.getsize(full_path) > 1024 * 1024:
                                FileService.logger.warning(
                                    f"Skipping large file {relative_path}: "
                                    f"size > 1MB ({os.path.getsize(full_path)} bytes)"
                                )
                                continue

                            outfile.write(f"# File: {relative_path}\n\n")
                            file_content = FileService.detect_and_read_file(full_path)
                            outfile.write(file_content + "\n\n")
                            files_processed += 1

                            FileService.logger.debug(f"Processed file: {relative_path}")

                        except Exception as e:
                            FileService.logger.error(f"Error processing file {file}: {e}")
                            continue

            FileService.logger.info(f"Successfully merged {files_processed} files into {output_file}")

            if files_processed == 0:
                warning_msg = "No files were processed during merge"
                FileService.logger.warning(warning_msg)
                raise FileServiceError(warning_msg)

            return output_file

        except FileServiceError:
            raise
        except Exception as e:
            error_msg = f"Failed to merge repository files: {str(e)}"
            FileService.logger.error(error_msg)
            raise FileServiceError(error_msg)
