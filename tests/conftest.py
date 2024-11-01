import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_settings():
    with patch('app.core.config.settings') as mock_settings:
        mock_settings.REDIS_HOST = "localhost"
        mock_settings.REDIS_PORT = 6379
        mock_settings.GITHUB_TOKEN = "test_token"
        mock_settings.OPENAI_API_KEY = "test_key"
        yield mock_settings
