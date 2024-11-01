from fastapi import APIRouter

from app.models.request_models import ReviewRequest
from app.services.openai_service import OpenAIService
from app.services.repository_service import RepositoryService

router = APIRouter()


@router.post("/review")
async def review_code(request: ReviewRequest):
    processing_result = await RepositoryService.process_repository(
        github_url=request.github_repo_url
    )

    response_from_ai = await OpenAIService.get_response(
        task_description=request.assignment_description,
        file_path=processing_result["merged_filepath"],
        level=request.candidate_level,
    )

    return [processing_result["found_files"], response_from_ai]
