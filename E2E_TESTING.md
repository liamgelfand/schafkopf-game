# End-to-End Testing Guide

## Quick Start

### 1. Start Docker Containers

```bash
# From project root
docker-compose up -d

# Wait for services to be ready (check logs)
docker-compose logs -f backend
# Press Ctrl+C when you see "Application startup complete"
```

### 2. Run E2E Tests

```bash
cd backend
pytest tests/test_e2e_docker.py -v -m e2e_docker
```

### 3. Stop Containers

```bash
# From project root
docker-compose down
```

## Complete Commands

### Full Test Suite (Recommended Workflow)

```bash
# 1. Run fast unit/integration tests first (no Docker needed)
cd backend
pytest tests/ -v -m "not e2e_docker"

# 2. Start Docker for E2E tests
cd ..
docker-compose up -d

# 3. Wait for services (check logs)
docker-compose logs backend | grep -i "startup\|ready\|error" | tail -20

# 4. Run E2E Docker tests
cd backend
pytest tests/test_e2e_docker.py -v -m e2e_docker

# 5. Cleanup
cd ..
docker-compose down
```

### One-Liner (All Tests)

```bash
# From project root
docker-compose up -d && \
sleep 5 && \
cd backend && \
pytest tests/ -v && \
cd .. && \
docker-compose down
```

## Test Structure

### Unit/Integration Tests (32 tests)
- ✅ Fast (< 1 second)
- ✅ No Docker needed
- ✅ Test game logic directly
- ✅ Use in-memory SQLite

### E2E Docker Tests (6+ tests)
- ✅ Test full API stack
- ✅ Real HTTP requests
- ✅ Real PostgreSQL database
- ✅ Complete user flows
- ⚠️ Requires Docker running
- ⚠️ Slower (network calls)

## What Gets Tested

### E2E Docker Tests Cover:
1. ✅ API health check
2. ✅ User registration
3. ✅ User login & JWT tokens
4. ✅ Room creation
5. ✅ Room joining (multiple players)
6. ✅ Full game flow (4 players, ready, start)
7. ✅ Room listing

## Troubleshooting

### "Connection refused" errors
```bash
# Check if backend is running
docker-compose ps
curl http://localhost:8000/docs

# Restart if needed
docker-compose restart backend
```

### Tests timeout
```bash
# Check API is responding
curl http://localhost:8000/api/auth/register -X POST -H "Content-Type: application/json" -d '{"username":"test","email":"test@test.com","password":"test"}'

# Increase timeout in test file if needed
```

### Database errors
```bash
# Check database health
docker-compose ps db
docker-compose logs db

# Recreate if needed
docker-compose down -v
docker-compose up -d
```

## Best Practices

1. **Run unit tests first** - Get fast feedback
2. **Run E2E before deployment** - Catch integration issues
3. **Clean up after tests** - Consider adding cleanup logic
4. **Use in CI/CD** - Automate E2E tests in pipeline
5. **Test in isolation** - Each test should be independent

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start Docker
        run: docker-compose up -d
      - name: Wait for services
        run: sleep 10
      - name: Run E2E tests
        run: |
          cd backend
          pip install -r requirements-test.txt
          pytest tests/test_e2e_docker.py -v -m e2e_docker
      - name: Stop Docker
        run: docker-compose down
```


