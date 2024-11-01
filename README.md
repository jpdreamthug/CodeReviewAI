# CodeReviewAI

AI-powered code review tool that analyzes GitHub repositories and provides detailed feedback using OpenAI API.

## Quick Start

### Docker Setup (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/code-review-ai
cd code-review-ai

# 2. Create .env file with your tokens
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
REDIS_HOST=redis
REDIS_PORT=6379

# 3. Run the application
docker-compose up --build
```

### Local Setup
```bash
# 1. Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 2. Install dependencies
poetry install

# 3. Set REDIS_HOST=localhost in .env file

# 4. Run Redis
docker run -d -p 6379:6379 redis:alpine

# 5. Run the application
poetry run uvicorn app.main:app --reload
```

## Usage

```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_description": "Backend service",
    "github_repo_url": "https://github.com/username/repo",
    "candidate_level": "Middle"
  }'
```

## Scaling Solution

To handle increased load (100+ requests/minute and large repositories), the following improvements would be implemented:

### Current Limitations
- OpenAI API rate limits and costs
- Single-threaded processing
- Large repository processing time
- GitHub API rate limits

### Proposed Solutions

1. **Request Processing**
   - Implement RabbitMQ for asynchronous request processing
   - Add worker nodes to process requests from the queue
   - Distribute load across multiple instances

2. **API Management**
   - Use multiple OpenAI accounts with API key rotation
   - Implement token bucket rate limiting
   - Cache common repository analysis results

3. **Repository Processing**
   - Break large repositories into smaller chunks
   - Process files in parallel
   - Implement file filtering and priority processing

4. **Infrastructure**
   - Use load balancers for request distribution
   - Add read replicas for Redis cache
   - Implement health checks and auto-scaling

```
                   ┌─── Worker 1 ──┐
Client → API → RabbitMQ ─── Worker 2 ──→ Cache → Response
                   └─── Worker 3 ──┘
```

This architecture would allow for:
- Scalable request handling
- Reliable processing of large repositories
- Cost-effective API usage
- Better resource utilization