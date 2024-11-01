from unittest.mock import patch


def test_review_code_success(client):
    request_data = {
        "assignment_description": "Test task",
        "github_repo_url": "https://github.com/test/repo",
        "candidate_level": "Junior"
    }

    with patch('app.services.repository_service.RepositoryService.process_repository') as mock_repo, \
            patch('app.services.openai_service.OpenAIService.get_response') as mock_ai:
        mock_repo.return_value = {
            "merged_filepath": "test.md",
            "found_files": ["test.py"]
        }
        mock_ai.return_value = "Code review result"

        response = client.post("/review", json=request_data)
        assert response.status_code == 200
        assert len(response.json()) == 2


def test_review_code_invalid_url(client):
    request_data = {
        "assignment_description": "Test task",
        "github_repo_url": "not-a-url",
        "candidate_level": "Junior"
    }

    response = client.post("/review", json=request_data)
    assert response.status_code == 422


def test_review_code_invalid_level(client):
    request_data = {
        "assignment_description": "Test task",
        "github_repo_url": "https://github.com/test/repo",
        "candidate_level": "Wrong"
    }

    response = client.post("/review", json=request_data)
    assert response.status_code == 422
