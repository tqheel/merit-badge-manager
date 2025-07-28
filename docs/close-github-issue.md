# Close GitHub Issue Functionality

## Overview

The MCP server now includes functionality to close GitHub issues by issue number. This feature allows you to programmatically close issues that have been completed or are no longer needed.

## API Endpoint

### POST `/close-issue`

Closes a GitHub issue by its issue number.

#### Request Body

```json
{
  "issue_number": 123,
  "reason": "completed"
}
```

#### Parameters

- `issue_number` (required): The GitHub issue number to close
- `reason` (optional): Reason for closing the issue. Valid values:
  - `"completed"` (default): Issue was successfully completed
  - `"not_planned"`: Issue will not be implemented

#### Response

```json
{
  "message": "GitHub issue #123 successfully closed",
  "github_issue": {
    "id": 123456789,
    "number": 123,
    "state": "closed",
    "state_reason": "completed",
    "url": "https://github.com/tqheel/merit-badge-manager/issues/123",
    "title": "Issue Title",
    "closed_at": "2025-01-27T22:59:42Z"
  }
}
```

#### Error Responses

- `404`: Issue not found
- `500`: GitHub token not configured or other server errors

## Usage Examples

### Using curl

```bash
# Close issue as completed
curl -X POST http://localhost:8000/close-issue \
  -H "Content-Type: application/json" \
  -d '{"issue_number": 123, "reason": "completed"}'

# Close issue as not planned
curl -X POST http://localhost:8000/close-issue \
  -H "Content-Type: application/json" \
  -d '{"issue_number": 456, "reason": "not_planned"}'
```

### Using Python (async)

```python
import aiohttp
import asyncio

async def close_issue(issue_number, reason="completed"):
    url = "http://localhost:8000/close-issue"
    payload = {"issue_number": issue_number, "reason": reason}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json()

# Usage
result = await close_issue(123, "completed")
```

### Using Python (synchronous with requests)

```python
import requests

def close_issue(issue_number, reason="completed"):
    url = "http://localhost:8000/close-issue"
    payload = {"issue_number": issue_number, "reason": reason}
    
    response = requests.post(url, json=payload)
    return response.json()

# Usage
result = close_issue(123, "completed")
```

## Configuration

Make sure your `.env` file has the required GitHub configuration:

```bash
# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=tqheel/merit-badge-manager
```

The GitHub token needs the following permissions:
- `repo` scope (for closing issues)

## Integration with MCP

This functionality follows the Merit Badge Manager project specifications:
- Includes issue number in commit messages (when applicable)
- Uses descriptive function and variable names
- Includes proper error handling
- Follows the existing code patterns in the MCP server

## Testing

The functionality includes tests in `tests/test_mcp_server.py`:
- Tests the `CloseIssueRequest` model validation
- Verifies default parameter handling
- Validates custom reason parameter handling

Run tests with:
```bash
python tests/test_mcp_server.py
```

## Example Script

See `scripts/close_issue_example.py` for a complete working example of how to use the close issue functionality.
