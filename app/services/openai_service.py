import os
import logging
from openai import APIError, RateLimitError, APIConnectionError
from fastapi import HTTPException
from openai import AsyncOpenAI
from app.core.config import settings
from app.utils.prompt import code_review_prompt
from app.services.cache_service import cache_service


class OpenAIService:
    logger = logging.getLogger("openai_service")

    @staticmethod
    def format_prompt(task_description: str, file_content: str, level: str) -> str:
        return code_review_prompt.format(
            project_topic=task_description,
            developer_level=level,
            project_code=file_content,
        )

    @staticmethod
    def read_file(file_path: str) -> str:
        with open(file_path, "r") as file:
            return file.read()

    @staticmethod
    async def get_response(task_description: str, file_path: str, level: str) -> str:
        try:
            cache_key = cache_service.generate_cache_key(
                file_path, task_description, level
            )
            cached_response = await cache_service.get_cache(cache_key)

            if cached_response:
                return cached_response

            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            file_content = OpenAIService.read_file(file_path)
            formatted_prompt = OpenAIService.format_prompt(
                task_description, file_content, level
            )

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": formatted_prompt}],
            )

            result = response.choices[0].message.content
            await cache_service.set_cache(cache_key, result)

            return result

        except RateLimitError:
            raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded")
        except APIConnectionError:
            raise HTTPException(status_code=503, detail="OpenAI API unavailable")
        except APIError as e:
            raise HTTPException(status_code=500, detail=str(e))
