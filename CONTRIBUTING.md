# Contributing to Telegram Evolution API

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](./CODE_OF_CONDUCT.md). Please read it before contributing.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected vs actual behavior**
- **Environment details**: OS, Python version, Docker version
- **Logs or error messages** (with sensitive data redacted)

Example:

```markdown
**Describe the bug**
Instance fails to reconnect after restart with FloodWaitError.

**To Reproduce**
1. Create instance and authenticate
2. Send 50 messages rapidly
3. Restart the container
4. Check instance status

**Expected behavior**
Instance should reconnect and respect FloodWait delay.

**Environment**
- OS: Ubuntu 22.04
- Python: 3.11
- Docker: 24.0.5
```

### Suggesting Features

Feature suggestions are welcome! Please include:

- **Use case**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches you've thought about

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install dev dependencies**: `pip install -e ".[dev]"`
3. **Make your changes** following the coding standards below
4. **Add tests** for new functionality
5. **Ensure tests pass**: `pytest`
6. **Update documentation** if needed
7. **Submit a pull request** with a clear description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/azeezalhajj570-ai/telegram-evolution-api.git
cd telegram-evolution-api

# Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Start dependencies (PostgreSQL + Redis)
docker compose up -d postgres redis

# Run migrations
alembic upgrade head

# Run tests
pytest
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use type hints for all function signatures
- Maximum line length: 120 characters
- Use double quotes for strings

### Code Organization

- **API routes** go in `app/api/`
- **Business logic** goes in `app/services/`
- **Database models** go in `app/db/models.py`
- **Pydantic schemas** go in `app/schemas/`
- **Security utilities** go in `app/security/`

### Error Handling

- Use specific exception types, not bare `except Exception`
- Return structured error responses: `{"error": "error_code", "detail": "message"}`
- Never log sensitive data (OTP codes, passwords, session strings, API keys)

### Security Rules

- **Never commit** `.env` files or credentials
- **Never log** OTP codes, 2FA passwords, API keys, or session strings
- **Hash** API keys before storage using bcrypt
- **Encrypt** session strings using Fernet symmetric encryption
- **Sign** webhook payloads with HMAC-SHA256

## Testing

### Writing Tests

- Tests go in the `tests/` directory
- Name test files: `test_<module>.py`
- Use descriptive test names: `test_send_message_returns_message_id()`
- Mock external services (Telegram API, Redis) in unit tests
- Use fixtures from `conftest.py` for common setup

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_messages.py

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run with verbose output
pytest -v
```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:

```
feat(messages): add support for voice messages
fix(auth): handle phone_code_hash mismatch on verify
docs(readme): update API examples with new endpoints
test(webhooks): add tests for HMAC signature verification
```

## Branch Strategy

- `main` — stable release branch
- Feature branches — `feat/<description>`
- Bug fix branches — `fix/<description>`
- Documentation branches — `docs/<description>`

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with new release notes
3. Create a git tag: `git tag v0.x.0`
4. Push tag: `git push origin v0.x.0`

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for general questions
- Review existing documentation before asking

Thank you for contributing!
