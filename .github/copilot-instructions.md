# GitHub Copilot Instructions

## Specifications
See the [specification document](../spec.md) for detailed requirements and architecture.

## When starting new terminal Sessions for Copilot:
- Always verify that the new terminal session is finished initializing before running any commands.
- Ensure that the Python Virtual Environment is created and activated before running the application or Python scripts, tests, and commands.
- If the virtual environment is not activated, run `source venv/bin/activate` to activate it.
- If the virtual environment does not exist, create it using `python3.12 -m venv venv`.
- Install dependencies using `pip install -r requirements.txt`.

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
- Update compatible dependencies that are not breaking changes.
- Label all Github issues that are sub-issues of Feature requests as `user story`.
- Use YAML block literal syntax (|) for multi-line content in feature/bug templates to prevent content truncation.
- When working with youth roster functionality, ensure integration with adult roster system through proper foreign key relationships.
- Test both adult and youth database schemas when making changes to ensure cross-system compatibility.
- Validate Scout-to-counselor assignment functionality when modifying merit badge progress tracking.
- Include parent/guardian contact validation when working with Scout data.
- Test validation views for both adult and youth systems to ensure data quality checks function properly.
- Use the centralized database location at `/database/merit_badge_manager.db` for all database operations.
- Import database utilities from `web-ui/database_utils.py` when working with web UI components to ensure consistent database access.
- Use `get_database_path()`, `get_database_connection()`, and `database_exists()` functions from database_utils instead of hardcoding database paths.

## Never:
- Never include any passwords, API keys, or sensitive information in the codebase except in secure configuration files that are not committed to the repository.
- Never hard-code values that should be configurable.
- Never commit code that does not pass the automated tests.
- Never use global variables unless absolutely necessary.
- Never include any PII or or any other Troop data in the codebase, test cases, documentaion, comments, or Github issues.
- Never modify youth database schema without ensuring backward compatibility with adult roster system.
- Never delete Scout data without proper CASCADE DELETE constraints to maintain referential integrity.
- Never bypass parent/guardian contact validation when working with Scout information.
- Never create merit badge assignments without proper counselor validation from adult roster.
- Never create duplicate database files or hardcode database paths - always use the centralized database location at `/database/merit_badge_manager.db`.
- Never reference relative database paths like `merit_badge_manager.db` or `./merit_badge_manager.db` in web UI components - use the database_utils functions instead.