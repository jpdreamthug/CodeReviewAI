import logging
import os

from fastapi import HTTPException
from openai import AsyncOpenAI

from app.core.config import settings
from app.services.cache_service import cache_service
from app.utils.prompt import code_review_prompt


class OpenAIService:
    logger = logging.getLogger('openai_service')

    @staticmethod
    def format_prompt(task_description: str, file_content: str, level: str) -> str:
        try:
            return code_review_prompt.format(
                project_topic=task_description,
                developer_level=level,
                project_code=file_content
            )
        except Exception as e:
            OpenAIService.logger.error(f"Error formatting prompt: {e}")
            raise HTTPException(status_code=500, detail="Error formatting review prompt")

    @staticmethod
    def read_file(file_path: str) -> str:
        try:
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"File not found: {file_path}"
                )

            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            OpenAIService.logger.error(f"Error reading file: {e}")
            raise HTTPException(status_code=500, detail="Error reading file content")

    @staticmethod
    async def get_response(
            task_description: str,
            file_path: str,
            level: str
    ) -> str:
        try:
            cache_key = cache_service.generate_cache_key(file_path, task_description, level)
            cached_response = await cache_service.get_cache(cache_key)

            if cached_response:
                OpenAIService.logger.info("Using cached response")
                return cached_response

            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            file_content = OpenAIService.read_file(file_path)
            formatted_prompt = OpenAIService.format_prompt(task_description, file_content, level)

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": formatted_prompt}
                ]
            )

            result = response.choices[0].message.content
            await cache_service.set_cache(cache_key, result)

            return result

        except HTTPException:
            raise
        except Exception as e:
            OpenAIService.logger.error(f"OpenAI API error: {e}")
            raise HTTPException(status_code=500, detail="Error generating code review")
