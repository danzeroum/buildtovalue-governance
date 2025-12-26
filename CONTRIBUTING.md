# Contributing to BuildToValue

Thank you for considering contributing! BuildToValue is a community-driven project.

## How to Contribute

### 1. Reporting Bugs

- Use GitHub Issues
- Check if bug already exists
- Provide: OS, Python version, steps to reproduce, expected vs actual behavior

### 2. Suggesting Features

- Open a Discussion first (not an Issue)
- Explain use case and why it's valuable
- Consider: Does it align with ISO 42001 compliance?

### 3. Submitting Pull Requests

#### Setup Development Environment

Fork and clone
git clone https://github.com/YOUR_USERNAME/btv-framework.git
cd btv-framework

Create virtual environment
python3 -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

Install dev dependencies
pip install -r requirements-dev.txt

Run tests
pytest tests/ -v

text

#### Code Style

- **Formatter**: Black (line length: 100)
- **Linter**: Flake8
- **Type Hints**: Required for public APIs
- **Docstrings**: Google style

Format code
black src/ tests/

Lint
flake8 src/ tests/ --max-line-length=100

Type check
mypy src/

text

#### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

feat: add support for MongoDB backend
fix: prevent BOLA attack in tenant isolation
docs: update API reference for v7.3
test: add integration tests for enforcement engine

text

#### Pull Request Checklist

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Code formatted (`black .`)
- [ ] No linting errors (`flake8`)
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated
- [ ] Branch is rebased on latest `main`

### 4. Documentation

Improvements to docs are highly valued!

- Typo fixes: Open PR directly
- New guides: Open Discussion first
- API reference: Auto-generated from docstrings

## Project Structure

src/
├── domain/ # Business entities (AISystem, Task)
├── core/ # Core logic (enforcement, registry)
├── interface/ # API layer (FastAPI, auth)
├── intelligence/ # AI agents (risk assessment)
└── compliance/ # Compliance tools (RAG, ledger)

text

## Development Workflow

1. **Create feature branch**: `git checkout -b feat/your-feature`
2. **Make changes**: Follow code style
3. **Add tests**: Coverage must stay > 80%
4. **Run tests**: `pytest tests/ --cov=src`
5. **Commit**: Use conventional commits
6. **Push**: `git push origin feat/your-feature`
7. **Open PR**: Link to related issue

## Code Review Process

1. Maintainers review within 3 business days
2. At least 1 approval required
3. All CI checks must pass
4. Squash merge into `main`

## Community

- **Discord**: https://discord.gg/buildtovalue
- **Monthly Calls**: First Friday of each month (details in Discord)
- **Twitter**: [@BuildToValue](https://twitter.com/buildtovalue)

## License

By contributing, you agree that your contributions will be licensed under Apache 2.0.

---

**Questions?** Open a Discussion or ask in Discord #dev-help channel.