import pytest
from unittest.mock import patch, Mock

from app.services.openai_service import OpenAIService


def test_format_prompt():
    result = OpenAIService.format_prompt(
        "test task",
        "test code",
        "Junior"
    )
    assert isinstance(result, str)
    assert "test task" in result


@pytest.mark.asyncio
async def test_get_response(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("print('test')")

    mock_completion = Mock()
    mock_completion.choices = [Mock()]
    mock_completion.choices[0].message.content = "Review result"

    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_instance = Mock()
        mock_instance.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_instance

        result = await OpenAIService.get_response(
            "test task",
            str(test_file),
            "Junior"
        )
        assert isinstance(result, str)
