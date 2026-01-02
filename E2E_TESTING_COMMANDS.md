# E2E Testing Commands - Quick Reference

## 🚀 Complete Workflow

### Option 1: Step-by-Step (Recommended for first time)

```powershell
# 1. Start Docker containers
docker-compose up -d

# 2. Wait for services (check logs)
docker-compose logs backend | Select-String -Pattern "startup|Uvicorn|Application" | Select-Object -Last 5

# 3. Verify API is running
Invoke-WebRequest -Uri http://localhost:8000/docs -UseBasicParsing

# 4. Run E2E tests
cd backend
pytest tests/test_e2e_docker.py -v -m e2e_docker

# 5. Cleanup
cd ..
docker-compose down
```

### Option 2: One-Liner

```powershell
# Complete workflow in one command
docker-compose up -d; Start-Sleep -Seconds 10; cd backend; pytest tests/test_e2e_docker.py -v -m e2e_docker; cd ..; docker-compose down
```

## 📋 Individual Commands

### Start Docker
```powershell
docker-compose up -d
```

### Check Services Status
```powershell
docker-compose ps
```

### View Backend Logs
```powershell
docker-compose logs -f backend
# Press Ctrl+C to exit
```

### Run E2E Tests Only
```powershell
cd backend
pytest tests/test_e2e_docker.py -v -m e2e_docker
```

### Run All Tests (Unit + E2E)
```powershell
cd backend
pytest tests/ -v
```

### Run Unit Tests Only (No Docker)
```powershell
cd backend
pytest tests/ -v -m "not e2e_docker"
```

### Stop Docker
```powershell
docker-compose down
```

### Stop and Remove Volumes (Clean Slate)
```powershell
docker-compose down -v
```

## ✅ What Gets Tested

The E2E Docker tests verify:

1. ✅ **API Health** - Server is running and accessible
2. ✅ **User Registration** - Can create new users
3. ✅ **User Login** - Authentication and JWT tokens work
4. ✅ **Room Creation** - Can create game rooms
5. ✅ **Room Joining** - Multiple players can join
6. ✅ **Full Game Flow** - 4 players, ready up, game starts
7. ✅ **Room Listing** - Can view available rooms

## 🔍 Troubleshooting

### Connection Refused
```powershell
# Check if containers are running
docker-compose ps

# Restart backend
docker-compose restart backend

# Check logs for errors
docker-compose logs backend
```

### Tests Timeout
```powershell
# Verify API responds
curl http://localhost:8000/docs

# Or PowerShell
Invoke-WebRequest -Uri http://localhost:8000/docs
```

### Database Errors
```powershell
# Check database container
docker-compose ps db

# View database logs
docker-compose logs db

# Recreate everything
docker-compose down -v
docker-compose up -d
```

## 📊 Expected Results

**When tests pass:**
```
tests/test_e2e_docker.py::TestE2EDocker::test_api_health_check PASSED
tests/test_e2e_docker.py::TestE2EDocker::test_register_and_login PASSED
tests/test_e2e_docker.py::TestE2EDocker::test_create_room PASSED
tests/test_e2e_docker.py::TestE2EDocker::test_join_room PASSED
tests/test_e2e_docker.py::TestE2EDocker::test_full_game_flow_4_players PASSED
tests/test_e2e_docker.py::TestE2EDocker::test_list_rooms PASSED

================== 6 passed in X.XXs ==================
```

## 🎯 Best Practices

1. **Run unit tests first** (fast, no Docker)
2. **Start Docker for E2E** (slower, full stack)
3. **Clean up after** (stop containers)
4. **Use in CI/CD** (automate before deployment)


