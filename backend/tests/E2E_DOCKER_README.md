# Docker-Based E2E Tests

These are **true end-to-end tests** that require Docker containers to be running. They make actual HTTP requests to the API server.

## Prerequisites

1. **Docker and Docker Compose installed**
2. **Docker containers running** (backend, frontend, database)

## Running E2E Docker Tests

### Step 1: Start Docker Containers

```bash
# From project root
docker-compose up -d

# Wait for services to be healthy (check logs)
docker-compose logs -f backend
# Press Ctrl+C when you see "Application startup complete"
```

### Step 2: Run E2E Tests

```bash
cd backend

# Install test dependencies (if not already installed)
pip install -r requirements-test.txt

# Run only Docker E2E tests
pytest tests/test_e2e_docker.py -v -m e2e_docker

# Or run all tests (unit + E2E Docker)
pytest tests/ -v
```

### Step 3: Stop Containers (when done)

```bash
# From project root
docker-compose down
```

## Test Coverage

The E2E Docker tests cover:

1. **API Health Check** - Verifies API is running
2. **User Registration & Login** - Full auth flow
3. **Room Creation** - Creating game rooms
4. **Room Joining** - Multiple players joining
5. **Full Game Flow** - 4 players, ready up, game start
6. **Room Listing** - Viewing available rooms

## Configuration

You can override the API URL:

```bash
# Test against different environment
export API_URL=http://localhost:8000
pytest tests/test_e2e_docker.py -v
```

## What Makes These "True E2E"?

- ✅ Make **actual HTTP requests** to running server
- ✅ Test **full stack** (API → Database → Response)
- ✅ Test **real authentication** (JWT tokens)
- ✅ Test **real database** (PostgreSQL in Docker)
- ✅ Test **complete user flows** (register → login → play)

## Differences from Unit/Integration Tests

| Aspect | Unit/Integration Tests | E2E Docker Tests |
|--------|----------------------|------------------|
| **HTTP Requests** | ❌ No (test code directly) | ✅ Yes (httpx client) |
| **Database** | In-memory SQLite | Real PostgreSQL |
| **Docker Required** | ❌ No | ✅ Yes |
| **Speed** | Fast (< 1s) | Slower (network calls) |
| **Isolation** | High | Lower (shared DB) |
| **Use Case** | Development, CI | Pre-deployment, QA |

## Troubleshooting

### Tests fail with "Connection refused"

```bash
# Check if containers are running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Restart containers
docker-compose restart
```

### Tests fail with "timeout"

```bash
# Increase timeout in test_e2e_docker.py
# Or check if API is responding:
curl http://localhost:8000/docs
```

### Database connection errors

```bash
# Ensure database is healthy
docker-compose ps db

# Check database logs
docker-compose logs db

# Recreate database
docker-compose down -v
docker-compose up -d
```

## Best Practices

1. **Run unit tests first** - Fast feedback before E2E
2. **Run E2E tests before deployment** - Catch integration issues
3. **Clean up test data** - Tests create users/rooms (consider cleanup)
4. **Use unique identifiers** - Tests use random suffixes to avoid conflicts
5. **Run in CI/CD** - Automate E2E tests in your pipeline


