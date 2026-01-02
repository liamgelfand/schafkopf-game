# Testing Guide

## Backend Tests

### Setup
```bash
cd backend
pip install -r requirements-test.txt
```

### Test Categories

#### 1. Unit & Integration Tests (No Docker needed)
Fast tests that run without Docker:
```bash
# Run all unit/integration tests
pytest tests/ -v -m "not e2e_docker"

# Run specific categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e           # E2E game logic tests (no Docker)
```

#### 2. Docker-Based E2E Tests (Requires Docker)
True end-to-end tests hitting the running API:
```bash
# Start Docker containers first
docker-compose up -d

# Run E2E Docker tests
pytest tests/test_e2e_docker.py -v -m e2e_docker

# Stop containers when done
docker-compose down
```

### Run All Tests
```bash
# Unit/integration only (fast, no Docker)
pytest tests/ -v -m "not e2e_docker"

# Everything (requires Docker running)
docker-compose up -d && pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_game.py -v
pytest tests/test_bidding.py -v
pytest tests/test_e2e_docker.py -v -m e2e_docker
```

### Run with Coverage
```bash
pytest --cov=app tests/ -m "not e2e_docker"
```

### Test Files
- `tests/test_game.py` - Game logic tests (bidding, contracts, card dealing)
- `tests/test_auth.py` - Authentication and security tests
- `tests/test_bidding.py` - Bidding logic and contract hierarchy
- `tests/test_integration_game.py` - Integration tests
- `tests/test_e2e_game_flow.py` - E2E game logic tests (no Docker)
- `tests/test_e2e_docker.py` - **True E2E tests (requires Docker)**

## Frontend Tests

### Setup
```bash
cd frontend
npm install
```

### Run Tests
```bash
# Run tests in watch mode
npm test

# Run tests with UI
npm run test:ui

# Run tests once
npm test -- --run
```

### Test Files
- `src/__tests__/GameBoard.test.tsx` - GameBoard component tests

## Integration Testing

### Manual Testing Checklist

1. **User Registration/Login**
   - [ ] Register new user
   - [ ] Login with existing user
   - [ ] Token expires after 24 hours
   - [ ] Logout works correctly

2. **Room Management**
   - [ ] Create room from dashboard
   - [ ] Join room from dashboard
   - [ ] Redirect to specific room after create/join
   - [ ] 4 players can join a room
   - [ ] Ready up system works
   - [ ] Auto-start when all 4 ready

3. **Game Initialization**
   - [ ] All 4 players see correct player names
   - [ ] Each player sees themselves at bottom
   - [ ] Each player sees correct player index
   - [ ] Cards are dealt (8 cards per player)
   - [ ] Random starter is selected

4. **Bidding Phase**
   - [ ] Players can see their cards during bidding
   - [ ] Turn order is correct (clockwise)
   - [ ] Players can bid (Rufer, Wenz, Solo)
   - [ ] Players can pass
   - [ ] Bidding ends after 3 passes
   - [ ] Contract is set correctly

5. **Gameplay**
   - [ ] Cards can be played
   - [ ] Turn order is correct
   - [ ] Trick winner is determined correctly
   - [ ] All 8 tricks are played
   - [ ] Scores are calculated

6. **Disconnection Handling**
   - [ ] Player disconnection is handled gracefully
   - [ ] Other players are notified
   - [ ] Room cleanup works correctly
