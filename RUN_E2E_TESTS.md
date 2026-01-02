# Commands to Run E2E Tests

## Quick Start (Copy & Paste)

```bash
# 1. Start Docker containers
docker-compose up -d

# 2. Wait for services to be ready (check logs)
docker-compose logs backend | Select-String -Pattern "startup|ready|Uvicorn running" | Select-Object -Last 5

# 3. Run E2E Docker tests
cd backend
pytest tests/test_e2e_docker.py -v -m e2e_docker

# 4. Stop containers when done
cd ..
docker-compose down
```

## Detailed Steps

### Step 1: Start Docker Containers

```powershell
# From project root
docker-compose up -d
```

**Wait for services to be healthy:**
```powershell
# Check backend is running
docker-compose ps

# Watch logs until you see "Application startup complete"
docker-compose logs -f backend
# Press Ctrl+C when ready
```

### Step 2: Verify API is Running

```powershell
# Test API health
curl http://localhost:8000/docs

# Or in PowerShell
Invoke-WebRequest -Uri http://localhost:8000/docs -UseBasicParsing
```

### Step 3: Install Test Dependencies (if needed)

```powershell
cd backend
pip install -r requirements-test.txt
```

### Step 4: Run E2E Tests

```powershell
# Run only E2E Docker tests
pytest tests/test_e2e_docker.py -v -m e2e_docker

# Or run all tests (unit + E2E)
pytest tests/ -v
```

### Step 5: Cleanup

```powershell
cd ..
docker-compose down
```

## One-Liner Script (PowerShell)

```powershell
# Complete workflow
docker-compose up -d; Start-Sleep -Seconds 10; cd backend; pytest tests/test_e2e_docker.py -v -m e2e_docker; cd ..; docker-compose down
```

## What Gets Tested

The E2E Docker tests verify:

1. ✅ API is accessible and running
2. ✅ User registration works
3. ✅ User login and JWT tokens work
4. ✅ Room creation works
5. ✅ Multiple players can join rooms
6. ✅ Full game flow (4 players, ready up, game starts)
7. ✅ Room listing works

## Troubleshooting

### "Connection refused" error
```powershell
# Check containers are running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Restart if needed
docker-compose restart backend
```

### Tests timeout
```powershell
# Verify API responds
Invoke-WebRequest -Uri http://localhost:8000/api/auth/register -Method POST -ContentType "application/json" -Body '{"username":"test","email":"test@test.com","password":"test"}'
```

### Database errors
```powershell
# Check database
docker-compose ps db
docker-compose logs db

# Recreate if needed
docker-compose down -v
docker-compose up -d
```

## Expected Output

When tests pass, you should see:

```
tests/test_e2e_docker.py::TestE2EDocker::test_api_health_check PASSED
tests/test_e2e_docker.py::TestE2EDocker::test_register_and_login PASSED
tests/test_e2e_docker.py::TestE2EDocker::test_create_room PASSED
tests/test_e2e_docker.py::TestE2EDocker::test_join_room PASSED
tests/test_e2e_docker.py::TestE2EDocker::test_full_game_flow_4_players PASSED
tests/test_e2e_docker.py::TestE2EDocker::test_list_rooms PASSED

================== 6 passed in X.XXs ==================
```


