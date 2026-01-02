# Test Architecture Explanation

## Why Tests Pass Without Docker

The tests are organized into different categories:

### 1. **Unit Tests** (No Docker needed)
- `test_bidding.py` - Tests game logic directly (Game objects)
- `test_game.py` - Tests game mechanics
- `test_card_logic.py` - Tests card/deck logic
- These test **pure Python logic** - no API, no database, no Docker

### 2. **Integration Tests** (No Docker needed)
- `test_integration_game.py` - Tests multiple game components together
- Still tests **Game objects directly** - no HTTP requests

### 3. **"E2E" Tests** (Currently misnamed - No Docker needed)
- `test_e2e_game_flow.py` - Tests complete game flows
- **BUT**: These test `Game` objects directly, NOT API endpoints
- They're more like integration tests, not true E2E

### 4. **API Tests** (REQUIRE Docker or full app setup)
- `test_api_rooms.py` - Tests `/api/rooms/*` endpoints
- `test_api_auth.py` - Tests `/api/auth/*` endpoints
- These are **currently SKIPPED** because `APP_AVAILABLE = False`

## Why API Tests Are Skipped

Looking at `conftest.py`:
```python
try:
    from app.main import app  # This import might fail
    APP_AVAILABLE = True
except ImportError:
    APP_AVAILABLE = False  # Tests get skipped
```

The API tests check `APP_AVAILABLE` and skip if it's False.

## Running True E2E Tests

You have **two options**:

### Option 1: Run API Tests Without Docker (In-Memory DB)
The `conftest.py` already sets up an in-memory SQLite database. The API tests should work if:
1. All Python dependencies are installed
2. The app can be imported

**Try this:**
```bash
cd backend
pytest tests/test_api_rooms.py -v
```

If they still skip, check why `APP_AVAILABLE` is False.

### Option 2: Run True E2E Tests With Docker
For tests that hit the actual running API:

1. **Start Docker containers:**
```bash
docker-compose up -d
```

2. **Run tests against live API:**
```bash
# Set API URL to Docker container
export API_URL=http://localhost:8000

# Run E2E tests (you'd need to create these)
pytest tests/test_e2e_api.py -v
```

## Current Test Status

- ✅ **32 tests passing** - Unit/integration tests (no Docker needed)
- ⏭️ **12 tests skipped** - API tests (need app to be importable)

## What You Should Do

1. **Check why API tests are skipped:**
   ```bash
   cd backend
   python -c "from app.main import app; print('App available!')"
   ```

2. **If app imports successfully, API tests should run:**
   ```bash
   pytest tests/test_api_rooms.py -v
   ```

3. **For true Docker-based E2E tests**, you'd need:
   - Tests that make HTTP requests to `http://localhost:8000`
   - Docker containers running
   - These don't exist yet - the current "E2E" tests are misnamed

## Recommendation

The current setup is actually good:
- **Unit tests** run fast without Docker ✅
- **API tests** use in-memory DB (no Docker needed) ✅
- **True E2E tests** would need Docker, but aren't implemented yet

If you want true E2E tests that hit Docker, we should create a separate test file like `test_e2e_docker.py` that makes actual HTTP requests.


