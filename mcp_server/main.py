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
PUBLISHED_FEATURES_DIR = WORKITEMS_DIR / "published" / "features"

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

class GitHubIssueData(BaseModel):
    title: str
    body: str
    labels: list[str]

# Helper functions
async def load_feature_yml(yml_filename: str) -> Dict[str, Any]:
    """Load and parse a feature YAML file."""
    feature_file = FEATURES_DIR / yml_filename
    if not feature_file.exists():
        raise HTTPException(status_code=404, detail=f"Feature file {yml_filename} not found")
    
    async with aiofiles.open(feature_file, 'r') as f:
        content = await f.read()
    
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")

def convert_yml_to_github_issue(feature_data: Dict[str, Any]) -> GitHubIssueData:
    """Convert feature YAML data to GitHub issue format."""
    # Extract the feature request template data
    body_sections = feature_data.get("body", [])
    
    title = ""
    problem_statement = ""
    proposed_solution = ""
    additional_context = ""
    
    for section in body_sections:
        if section.get("type") == "textarea":
            field_id = section.get("id", "")
            placeholder = section.get("attributes", {}).get("placeholder", "")
            
            if field_id == "problem":
                problem_statement = placeholder
            elif field_id == "solution":
                proposed_solution = placeholder
            elif field_id == "context":
                additional_context = placeholder
    
    # Generate title from filename or description
    title = feature_data.get("description", "Feature Request")
    
    # Format GitHub issue body
    body = f"""## Problem Statement
{problem_statement}

## Proposed Solution
{proposed_solution}

## Additional Context
{additional_context}

---
*This issue was automatically created from feature request template.*
"""
    
    # Get labels from the YAML
    labels = feature_data.get("labels", ["enhancement"])
    
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

async def move_feature_to_published(yml_filename: str) -> bool:
    """Move the feature YAML file to the published directory."""
    source_file = FEATURES_DIR / yml_filename
    destination_file = PUBLISHED_FEATURES_DIR / yml_filename
    
    if not source_file.exists():
        raise HTTPException(status_code=404, detail=f"Source file {yml_filename} not found")
    
    # Ensure the published directory exists
    PUBLISHED_FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        shutil.move(str(source_file), str(destination_file))
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move file: {str(e)}")

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
        "published_dir_exists": PUBLISHED_FEATURES_DIR.exists()
    }



