"""
MCP server for Merit Badge Manager with GitHub integration following Anthropic schema and project specification.
"""

import os
import shutil
import yaml
import aiohttp
import aiofiles
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI(title="Merit Badge Manager MCP Server", version="0.1.0")

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "tqheel/merit-badge-manager")
WORKITEMS_DIR = Path(__file__).parent.parent / "workitems"
FEATURES_DIR = WORKITEMS_DIR / "features"
BUGS_DIR = WORKITEMS_DIR / "bugs"
PUBLISHED_FEATURES_DIR = WORKITEMS_DIR / "published" / "features"
PUBLISHED_BUGS_DIR = WORKITEMS_DIR / "published" / "bugs"

# Anthropic schema endpoints will be added here in future development.

@app.get("/")
def root():
    return {"message": "MCP server is running."}

# Request models
class FeatureRequest(BaseModel):
    title: str
    description: str

class PublishFeatureRequest(BaseModel):
    yml_filename: str

class PublishBugRequest(BaseModel):
    yml_filename: str

class GitHubIssueData(BaseModel):
    title: str
    body: str
    labels: list[str]

class CloseIssueRequest(BaseModel):
    issue_number: int
    reason: Optional[str] = "completed"

# Helper functions
async def load_workitem_yml(yml_filename: str, workitem_type: str = "feature") -> Dict[str, Any]:
    """Load and parse a workitem YAML file (feature or bug)."""
    if workitem_type == "feature":
        workitem_file = FEATURES_DIR / yml_filename
    elif workitem_type == "bug":
        workitem_file = BUGS_DIR / yml_filename
    else:
        raise HTTPException(status_code=400, detail=f"Invalid workitem type: {workitem_type}")
    
    if not workitem_file.exists():
        raise HTTPException(status_code=404, detail=f"{workitem_type.title()} file {yml_filename} not found")
    
    async with aiofiles.open(workitem_file, 'r') as f:
        content = await f.read()
    
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")

# Legacy function for backward compatibility
async def load_feature_yml(yml_filename: str) -> Dict[str, Any]:
    """Load and parse a feature YAML file."""
    return await load_workitem_yml(yml_filename, "feature")

def convert_yml_to_github_issue(workitem_data: Dict[str, Any]) -> GitHubIssueData:
    """Convert workitem YAML data (feature or bug) to GitHub issue format."""
    # Extract the template data
    body_sections = workitem_data.get("body", [])
    
    title = ""
    description_content = ""
    steps_content = ""
    expected_content = ""
    problem_content = ""
    solution_content = ""
    additional_context = ""
    
    for section in body_sections:
        if section.get("type") == "textarea":
            field_id = section.get("id", "")
            placeholder = section.get("attributes", {}).get("placeholder", "")
            
            # Bug report fields
            if field_id == "description":
                description_content = placeholder
            elif field_id == "steps":
                steps_content = placeholder
            elif field_id == "expected":
                expected_content = placeholder
            # Feature request fields
            elif field_id == "problem":
                problem_content = placeholder
            elif field_id == "solution":
                solution_content = placeholder
            elif field_id == "context":
                additional_context = placeholder
    
    # Generate title from description
    title = workitem_data.get("description", "Workitem")
    
    # Determine if this is a bug or feature and format accordingly
    labels = workitem_data.get("labels", [])
    if "bug" in labels:
        # Format as bug report
        body = f"""## Description
{description_content}

## Steps to Reproduce
{steps_content}

## Expected Behavior
{expected_content}

## Additional Context
{additional_context}

---
*This issue was automatically created from bug report template.*
"""
    else:
        # Format as feature request
        body = f"""## Problem Statement
{problem_content}

## Proposed Solution
{solution_content}

## Additional Context
{additional_context}

---
*This issue was automatically created from feature request template.*
"""
    
    return GitHubIssueData(title=title, body=body, labels=labels)

async def create_github_issue(issue_data: GitHubIssueData) -> Dict[str, Any]:
    """Create a GitHub issue using the GitHub API."""
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=500, detail="GitHub token not configured")
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": issue_data.title,
        "body": issue_data.body,
        "labels": issue_data.labels
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 201:
                return await response.json()
            else:
                error_text = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to create GitHub issue: {error_text}"
                )

async def close_github_issue(issue_number: int, reason: str = "completed") -> Dict[str, Any]:
    """Close a GitHub issue using the GitHub API."""
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=500, detail="GitHub token not configured")
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{issue_number}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    # Validate reason parameter
    if reason not in ["completed", "not_planned"]:
        reason = "completed"
    
    payload = {
        "state": "closed",
        "state_reason": reason
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.patch(url, json=payload, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"GitHub issue #{issue_number} not found"
                )
            else:
                error_text = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to close GitHub issue #{issue_number}: {error_text}"
                )

async def move_workitem_to_published(yml_filename: str, workitem_type: str = "feature") -> bool:
    """Move the workitem YAML file to the published directory."""
    if workitem_type == "feature":
        source_file = FEATURES_DIR / yml_filename
        destination_file = PUBLISHED_FEATURES_DIR / yml_filename
        published_dir = PUBLISHED_FEATURES_DIR
    elif workitem_type == "bug":
        source_file = BUGS_DIR / yml_filename
        destination_file = PUBLISHED_BUGS_DIR / yml_filename
        published_dir = PUBLISHED_BUGS_DIR
    else:
        raise HTTPException(status_code=400, detail=f"Invalid workitem type: {workitem_type}")
    
    if not source_file.exists():
        raise HTTPException(status_code=404, detail=f"Source file {yml_filename} not found")
    
    # Ensure the published directory exists
    published_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        shutil.move(str(source_file), str(destination_file))
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move file: {str(e)}")

# Legacy function for backward compatibility
async def move_feature_to_published(yml_filename: str) -> bool:
    """Move the feature YAML file to the published directory."""
    return await move_workitem_to_published(yml_filename, "feature")

# API Endpoints

@app.post("/publish-feature")
async def publish_feature_to_github(request: PublishFeatureRequest):
    """
    Publish a feature YAML file as a GitHub issue and move it to published directory.
    """
    try:
        # Load the feature YAML file
        feature_data = await load_feature_yml(request.yml_filename)
        
        # Convert to GitHub issue format
        issue_data = convert_yml_to_github_issue(feature_data)
        
        # Create the GitHub issue
        github_response = await create_github_issue(issue_data)
        
        # Move the file to published directory
        await move_feature_to_published(request.yml_filename)
        
        return {
            "message": "Feature successfully published to GitHub and moved to published directory",
            "github_issue": {
                "id": github_response.get("id"),
                "number": github_response.get("number"),
                "url": github_response.get("html_url"),
                "title": github_response.get("title")
            },
            "published_file": str(PUBLISHED_FEATURES_DIR / request.yml_filename)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/publish-bug")
async def publish_bug_to_github(request: PublishBugRequest):
    """
    Publish a bug YAML file as a GitHub issue and move it to published directory.
    """
    try:
        # Load the bug YAML file
        bug_data = await load_workitem_yml(request.yml_filename, "bug")
        
        # Convert to GitHub issue format
        issue_data = convert_yml_to_github_issue(bug_data)
        
        # Create the GitHub issue
        github_response = await create_github_issue(issue_data)
        
        # Move the file to published directory
        await move_workitem_to_published(request.yml_filename, "bug")
        
        return {
            "message": "Bug successfully published to GitHub and moved to published directory",
            "github_issue": {
                "id": github_response.get("id"),
                "number": github_response.get("number"),
                "url": github_response.get("html_url"),
                "title": github_response.get("title")
            },
            "published_file": str(PUBLISHED_BUGS_DIR / request.yml_filename)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/close-issue")
async def close_github_issue_endpoint(request: CloseIssueRequest):
    """
    Close a GitHub issue by issue number.
    """
    try:
        # Close the GitHub issue
        github_response = await close_github_issue(request.issue_number, request.reason)
        
        return {
            "message": f"GitHub issue #{request.issue_number} successfully closed",
            "github_issue": {
                "id": github_response.get("id"),
                "number": github_response.get("number"),
                "state": github_response.get("state"),
                "state_reason": github_response.get("state_reason"),
                "url": github_response.get("html_url"),
                "title": github_response.get("title"),
                "closed_at": github_response.get("closed_at")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/bugs")
async def list_unpublished_bugs():
    """List all unpublished bug YAML files."""
    try:
        if not BUGS_DIR.exists():
            return {"bugs": []}
        
        yml_files = [f.name for f in BUGS_DIR.glob("*.yml")]
        return {"bugs": yml_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing bugs: {str(e)}")

@app.get("/published-bugs")
async def list_published_bugs():
    """List all published bug YAML files."""
    try:
        if not PUBLISHED_BUGS_DIR.exists():
            return {"published_bugs": []}
        
        yml_files = [f.name for f in PUBLISHED_BUGS_DIR.glob("*.yml")]
        return {"published_bugs": yml_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing published bugs: {str(e)}")

@app.get("/bug/{yml_filename}")
async def get_bug_details(yml_filename: str):
    """Get details of a specific bug YAML file."""
    try:
        bug_data = await load_workitem_yml(yml_filename, "bug")
        issue_preview = convert_yml_to_github_issue(bug_data)
        
        return {
            "filename": yml_filename,
            "raw_data": bug_data,
            "github_preview": {
                "title": issue_preview.title,
                "body": issue_preview.body,
                "labels": issue_preview.labels
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bug details: {str(e)}")

@app.get("/features")
async def list_unpublished_features():
    """List all unpublished feature YAML files."""
    try:
        if not FEATURES_DIR.exists():
            return {"features": []}
        
        yml_files = [f.name for f in FEATURES_DIR.glob("*.yml")]
        return {"features": yml_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing features: {str(e)}")

@app.get("/published-features")
async def list_published_features():
    """List all published feature YAML files."""
    try:
        if not PUBLISHED_FEATURES_DIR.exists():
            return {"published_features": []}
        
        yml_files = [f.name for f in PUBLISHED_FEATURES_DIR.glob("*.yml")]
        return {"published_features": yml_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing published features: {str(e)}")

@app.get("/feature/{yml_filename}")
async def get_feature_details(yml_filename: str):
    """Get details of a specific feature YAML file."""
    try:
        feature_data = await load_feature_yml(yml_filename)
        issue_preview = convert_yml_to_github_issue(feature_data)
        
        return {
            "filename": yml_filename,
            "raw_data": feature_data,
            "github_preview": {
                "title": issue_preview.title,
                "body": issue_preview.body,
                "labels": issue_preview.labels
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting feature details: {str(e)}")

# Legacy endpoints (keep for backward compatibility)

@app.post("/features")
async def create_feature(feature: FeatureRequest):
    """Legacy endpoint for creating features (placeholder for GitHub Issue integration)."""
    return {"message": "Feature created (placeholder)", "feature": feature.dict()}

@app.post("/")
async def root_post(request: Request):
    """Handle POST requests at root."""
    data = await request.json()
    return JSONResponse(content={"received": data})

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "github_configured": bool(GITHUB_TOKEN),
        "features_dir_exists": FEATURES_DIR.exists(),
        "bugs_dir_exists": BUGS_DIR.exists(),
        "published_features_dir_exists": PUBLISHED_FEATURES_DIR.exists(),
        "published_bugs_dir_exists": PUBLISHED_BUGS_DIR.exists()
    }

@app.get("/endpoints")
async def list_endpoints():
    """List all available API endpoints."""
    return {
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "Root endpoint"
            },
            {
                "path": "/health",
                "method": "GET", 
                "description": "Health check endpoint"
            },
            {
                "path": "/endpoints",
                "method": "GET",
                "description": "List all available endpoints"
            },
            {
                "path": "/publish-feature",
                "method": "POST",
                "description": "Publish a feature YAML file as a GitHub issue"
            },
            {
                "path": "/publish-bug", 
                "method": "POST",
                "description": "Publish a bug YAML file as a GitHub issue"
            },
            {
                "path": "/close-issue",
                "method": "POST", 
                "description": "Close a GitHub issue by issue number"
            },
            {
                "path": "/features",
                "method": "GET",
                "description": "List all unpublished feature YAML files"
            },
            {
                "path": "/bugs",
                "method": "GET",
                "description": "List all unpublished bug YAML files"
            },
            {
                "path": "/published-features",
                "method": "GET",
                "description": "List all published feature YAML files"
            },
            {
                "path": "/published-bugs",
                "method": "GET",
                "description": "List all published bug YAML files"
            },
            {
                "path": "/feature/{yml_filename}",
                "method": "GET",
                "description": "Get details of a specific feature YAML file"
            },
            {
                "path": "/bug/{yml_filename}",
                "method": "GET",
                "description": "Get details of a specific bug YAML file"
            }
        ]
    }



