from pydantic import BaseModel, HttpUrl
from typing import Literal


class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: HttpUrl
    candidate_level: Literal["Junior", "Middle", "Senior"]
