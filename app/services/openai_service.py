import os

from app.core.config import settings

from openai import AsyncOpenAI

from app.utils.prompt import code_review_prompt


class OpenAIService:

    @staticmethod
    def format_prompt(task_description: str, file_content: str, level: str) -> str:
        return code_review_prompt.format(
            project_topic=task_description,
            developer_level=level,
            project_code=file_content
        )

    @staticmethod
    def read_file(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл по пути {file_path} не найден.")
        with open(file_path, 'r') as file:
            return file.read()

    @staticmethod
    async def get_response(
            task_description: str,
            file_path: str,
            level: str
    ) -> str:
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
        )
        file_content = OpenAIService.read_file(file_path)
        formatted_prompt = OpenAIService.format_prompt(task_description, file_content, level)

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": formatted_prompt}
            ]
        )
        print("response:", response)
        raw_response = response.choices[0].message.content

        return raw_response
