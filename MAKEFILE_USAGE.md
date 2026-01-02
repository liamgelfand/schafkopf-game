# Makefile Usage Guide

## Quick Start

```bash
# See all available commands
make help

# Run all fast tests (no Docker)
make test

# Run true E2E tests (with Docker)
make test-e2e-docker
```

## Testing Commands

### Backend Tests

```bash
# Run all backend tests (unit/integration/E2E game logic)
make test-backend

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run E2E game logic tests (no Docker)
make test-e2e

# Run true E2E Docker tests (requires Docker)
make test-e2e-docker

# Run all tests including Docker E2E
make test-all
```

### Frontend Tests

```bash
# Run frontend tests once
make test-frontend

# Run frontend tests in watch mode
make test-frontend-watch

# Run frontend tests with UI
make test-frontend-ui
```

### Coverage

```bash
# Generate coverage report (HTML + terminal)
make test-coverage

# Coverage in terminal only
make test-coverage-term
```

## Docker Commands

```bash
# Start Docker containers
make docker-up

# Stop Docker containers
make docker-down

# View all logs
make docker-logs

# View backend logs only
make docker-logs-backend

# Restart containers
make docker-restart

# Check container status
make docker-status
```

## Setup Commands

```bash
# Install all dependencies
make install

# Install backend only
make install-backend

# Install frontend only
make install-frontend
```

## Development Commands

```bash
# Start dev servers (foreground)
make dev

# Start dev servers (background)
make dev-background

# Rebuild containers
make rebuild
```

## Cleanup Commands

```bash
# Clean test artifacts
make clean

# Clean Docker volumes (removes all data)
make clean-docker
```

## CI/CD Commands

```bash
# Run CI test suite (no Docker E2E)
make ci-test

# Run pre-deployment tests (includes Docker E2E)
make pre-deploy-test
```

## Common Workflows

### Daily Development
```bash
# Run fast tests during development
make test-backend
```

### Before Committing
```bash
# Run all fast tests
make test

# Run frontend tests
make test-frontend
```

### Before Deployment
```bash
# Full test suite including Docker E2E
make test-all
```

### Setting Up New Environment
```bash
# Install everything
make install

# Start Docker
make docker-up

# Run all tests
make test-all
```

## Examples

### Example 1: Quick Test During Development
```bash
make test-unit
```

### Example 2: Full Test Before PR
```bash
make test
make test-frontend
```

### Example 3: Complete E2E Validation
```bash
make test-e2e-docker
```

### Example 4: Clean Start
```bash
make clean-docker
make docker-up
make test-all
```

## Notes

- **Windows**: Make sure you have `make` installed (use WSL, Git Bash, or install via Chocolatey)
- **Docker E2E tests**: Automatically start/stop Docker containers
- **Fast tests**: Unit/integration tests run without Docker
- **Coverage**: HTML reports are in `backend/htmlcov/index.html`

## Troubleshooting

### "make: command not found"
- **Windows**: Install via WSL, Git Bash, or Chocolatey: `choco install make`
- **Mac**: Usually pre-installed, or install via Homebrew: `brew install make`
- **Linux**: Usually pre-installed

### Docker commands fail
```bash
# Check Docker is running
docker ps

# Check docker-compose is available
docker-compose --version
```

### Tests fail
```bash
# Check dependencies are installed
make install

# Check Docker is running (for E2E tests)
make docker-status
```

