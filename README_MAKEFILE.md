# Makefile Setup and Usage

## Installing Make on Windows

### Option 1: Using Chocolatey (Recommended)
```powershell
# Install Chocolatey if you don't have it
# Then install make
choco install make
```

### Option 2: Using WSL (Windows Subsystem for Linux)
```powershell
# Install WSL
wsl --install

# Then use make from within WSL
wsl make test
```

### Option 3: Using Git Bash
Git Bash includes make. Just use Git Bash terminal instead of PowerShell.

### Option 4: Using Scoop
```powershell
scoop install make
```

## Quick Start

Once `make` is installed:

```bash
# See all available commands
make help

# Run all fast tests
make test

# Run E2E Docker tests
make test-e2e-docker
```

## All Available Commands

### Testing
- `make test` - Run all unit/integration tests (fast, no Docker)
- `make test-unit` - Run only unit tests
- `make test-integration` - Run only integration tests
- `make test-e2e` - Run E2E game logic tests (no Docker)
- `make test-e2e-docker` - Run true E2E tests (requires Docker)
- `make test-all` - Run all tests including Docker E2E
- `make test-backend` - Run all backend tests (no Docker)
- `make test-frontend` - Run frontend tests
- `make test-coverage` - Run tests with coverage report

### Docker
- `make docker-up` - Start Docker containers
- `make docker-down` - Stop Docker containers
- `make docker-logs` - View Docker logs
- `make docker-restart` - Restart Docker containers

### Setup
- `make install` - Install all dependencies
- `make install-backend` - Install backend dependencies
- `make install-frontend` - Install frontend dependencies

### Cleanup
- `make clean` - Clean test artifacts
- `make clean-docker` - Clean Docker volumes

## Example Workflows

### Daily Development
```bash
make test-backend
```

### Before Committing
```bash
make test
make test-frontend
```

### Before Deployment
```bash
make test-all
```

## Windows-Specific Notes

If `make` is not available, you can use the equivalent commands directly:

### Instead of `make test`
```powershell
cd backend
pytest tests/ -v -m "not e2e_docker"
```

### Instead of `make test-e2e-docker`
```powershell
docker-compose up -d
Start-Sleep -Seconds 10
cd backend
pytest tests/test_e2e_docker.py -v -m e2e_docker
cd ..
docker-compose down
```

### Instead of `make docker-up`
```powershell
docker-compose up -d
```

See `MAKEFILE_USAGE.md` for complete documentation.

