# How to Run Tests

## Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Test Categories

### Unit Tests (No dependencies, fast)
```bash
pytest tests/test_bidding.py tests/test_game.py tests/test_card_logic.py tests/test_auth.py -v
```

### Integration Tests
```bash
pytest tests/test_integration_game.py -v
```

### E2E Tests (Game flows)
```bash
pytest tests/test_e2e_game_flow.py -v
```

### API Tests (Require full app)
```bash
pytest tests/test_api_*.py -v
```

### WebSocket Tests
```bash
pytest tests/test_websocket_handlers.py -v
```

### BDD Tests
```bash
pytest tests/test_bdd_*.py -v
```

## Test Markers

Tests are marked for easy filtering:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only E2E tests
pytest -m e2e

# Run only BDD tests
pytest -m bdd
```

## Output Formats

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Coverage report
pytest --cov=app --cov-report=html
# Then open htmlcov/index.html in browser
```

## Common Issues

### Missing Dependencies
If you see `ModuleNotFoundError`, install dependencies:
```bash
pip install -r requirements-test.txt
```

### Database Errors
Tests use in-memory SQLite, so no database setup needed.

### Fixture Errors
If E2E tests fail with "fixture not found", they require full app dependencies.
Unit tests should work without them.


