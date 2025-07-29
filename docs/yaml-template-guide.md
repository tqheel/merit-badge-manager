# YAML Template Guide for GitHub Issue Creation

## Overview

This guide provides templates and best practices for creating feature and bug YAML files that will be published as GitHub issues through the MCP server.

## Critical Formatting Requirements

### ✅ Multi-line Content Formatting

**Always use YAML block literal syntax (`|`) for multi-line placeholder content:**

```yaml
placeholder: |
  Multi-line content should use this format
  to ensure complete content extraction
  and prevent truncation during parsing.
```

### ❌ Avoid Single-line Long Content

**Never use single-line formatting for long content:**

```yaml
# This will cause content truncation
placeholder: Very long single-line content that exceeds reasonable length limits and may be truncated during YAML parsing causing empty sections in published GitHub issues.
```

## Feature Request Template

```yaml
name: Feature Name
description: Brief description of the feature
labels: [enhancement, user story]
body:
  - type: markdown
    attributes:
      value: |
        ## Feature Name
        Brief introduction to the feature request.
  - type: textarea
    id: problem
    attributes:
      label: Problem Statement
      description: What problem are you trying to solve?
      placeholder: |
        Describe the problem or need that this feature addresses.
        Include context about current limitations or pain points.
        Explain why this feature is important for the project.
    validations:
      required: true
  - type: textarea
    id: solution
    attributes:
      label: Proposed Solution
      description: How would you like to see this solved?
      placeholder: |
        Describe your proposed solution in detail.
        Include implementation approach and key components.
        Explain how this solution addresses the problem.
    validations:
      required: true
  - type: textarea
    id: context
    attributes:
      label: Additional Context
      description: Add any other context, screenshots, or references here.
      placeholder: |
        Technical Requirements:
        - List specific technical requirements
        - Include any dependencies or constraints
        - Note compliance requirements
        
        Architecture Components:
        - Describe key components
        - Outline integration points
        - Define interfaces or APIs
        
        Success Criteria:
        - Define measurable outcomes
        - Include testing requirements
        - Specify acceptance criteria
```

## Bug Report Template

```yaml
name: Bug Name
description: Brief description of the bug
labels: [bug]
body:
  - type: markdown
    attributes:
      value: |
        ## Bug Report
        Brief introduction to the bug report.
  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: What happened?
      placeholder: |
        Provide a clear and concise description of the bug.
        Include what you expected to happen vs. what actually happened.
        Mention any error messages or unexpected behavior.
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: How can we reproduce this issue?
      placeholder: |
        1. Go to '...'
        2. Click on '...'
        3. Scroll down to '...'
        4. See error
        
        Include specific commands, inputs, or actions that trigger the bug.
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should have happened?
      placeholder: |
        Describe what you expected to happen.
        Include any relevant specifications or documentation.
        Explain the correct behavior based on requirements.
    validations:
      required: true
  - type: textarea
    id: context
    attributes:
      label: Additional Context
      description: Add any other context about the problem here.
      placeholder: |
        Environment Details:
        - Operating System: [e.g. macOS 14, Windows 11, Ubuntu 22.04]
        - Python Version: [e.g. 3.12.1]
        - Virtual Environment: [Active/Inactive]
        
        Error Logs:
        ```
        [Paste any relevant error messages or logs here]
        ```
        
        Screenshots:
        [Attach any relevant screenshots]
        
        Related Issues:
        - Link to any related issues or pull requests
```

## Validation Checklist

Before publishing YAML files, verify:

- [ ] All multi-line content uses `|` block literal syntax
- [ ] No single-line content exceeds 80 characters
- [ ] All required fields have substantial placeholder content
- [ ] Labels are appropriate (enhancement, user story, bug)
- [ ] File follows naming convention: `##-description.yml`

## Testing Locally

Test YAML files before publishing:

```bash
# Activate virtual environment
source venv/bin/activate

# Test YAML parsing
python3 -c "
import yaml
with open('workitems/features/your-file.yml', 'r') as f:
    data = yaml.safe_load(f)
    print('YAML parsed successfully')
    
# Test GitHub issue conversion
from mcp_server.main import convert_yml_to_github_issue
issue = convert_yml_to_github_issue(data)
print(f'Title: {issue.title}')
print(f'Content length: {len(issue.body)} chars')
"
```

## Common Issues and Solutions

### Empty GitHub Issue Sections
- **Cause**: Single-line formatting or content truncation
- **Solution**: Use `|` block literal syntax for all multi-line content

### YAML Parsing Errors
- **Cause**: Invalid YAML syntax or indentation
- **Solution**: Validate YAML syntax and ensure consistent indentation

### Missing Content
- **Cause**: Empty placeholder fields
- **Solution**: Ensure all textarea fields have substantial placeholder content

## Best Practices

1. **Content Length**: Keep placeholder content between 100-500 characters per section
2. **Formatting**: Use consistent indentation (2 spaces)
3. **Structure**: Follow the template structure exactly
4. **Testing**: Always test locally before publishing
5. **Naming**: Use descriptive filenames with number prefixes

---

**Remember**: The placeholder text becomes the actual content in the GitHub issue, so write it as if it's the final content, not just an example.
