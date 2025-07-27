# GitHub Copilot Instructions

## Specifications
See the [specification document](spec.md) for detailed requirements and architecture.

## Always:
- Follow the coding standards and best practices outlined in the specification document.
Include issue number in all commit messages.
- Use descriptive variable and function names.
- Write modular, reusable code.
- Write clear and concise commit messages that describe the changes made.
- Include tests for new features and bug fixes.
- Update documentation as needed to reflect changes in functionality.
- Generate a new test case for every GitHub issue created.
- Ensure the Python Virtual Environment is created and activated before running the application or Python scripts, tests and commands.
- Add new dependencies to the `requirements.txt` file and ensure they are installed in the virtual environment.
- Generate change scripts for database schema changes and ensure they are applied to the SQLite database.

## Never
- Never include any passwords, API keys, or sensitive information in the codebase except in secure configuration files that are not committed to the repository.
- Never hard-code values that should be configurable.
- Never commit code that does not pass the automated tests.
- Never use global variables unless absolutely necessary.
- Never include any PII or or any other Troop data in the codebase, test cases, documentaion, comments, or Github issues.