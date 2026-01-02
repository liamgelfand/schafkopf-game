# Test Suite Documentation

## Test Structure

This test suite includes three types of tests:

### 1. Unit Tests
- **Location**: `test_*.py` files
- **Purpose**: Test individual functions and methods in isolation
- **Examples**: 
  - `test_game.py` - Game logic unit tests
  - `test_auth.py` - Authentication unit tests
  - `test_bidding.py` - Bidding logic unit tests
  - `test_card_logic.py` - Card/deck logic tests

### 2. BDD Tests (Behavior Driven Development)
- **Location**: `test_bdd_*.py` and `features/*.feature`
- **Purpose**: Test behavior using Given-When-Then scenarios
- **Examples**:
  - `test_bdd_bidding.py` - Bidding behavior scenarios
  - `features/bidding.feature` - Gherkin feature definitions

### 3. E2E Tests (End-to-End)
- **Location**: `test_e2e_*.py` and `test_integration_*.py`
- **Purpose**: Test complete workflows and API integration
- **Examples**:
  - `test_e2e_game_flow.py` - Complete game flows
  - `test_api_*.py` - API endpoint tests
  - `test_integration_game.py` - Integration tests

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test types
```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# E2E tests
pytest -m e2e

# BDD tests
pytest -m bdd
```

### Run specific test file
```bash
pytest tests/test_bidding.py
```

### Run with verbose output
```bash
pytest -v
```

## Test Coverage

Current test coverage includes:
- ✅ Game initialization and player management
- ✅ Card dealing and deck management
- ✅ Bidding phase logic
- ✅ Contract ranking and validation
- ✅ Called ace validation for Rufer
- ✅ Reshuffle logic
- ✅ Authentication API
- ✅ Room management API
- ⚠️ WebSocket handlers (partial)
- ⚠️ Card play logic (needs more tests)
- ⚠️ Trick completion (needs more tests)

## Adding New Tests

### Unit Test Example
```python
def test_new_feature():
    """Test description"""
    # Arrange
    game = Game("test")
    
    # Act
    result = game.some_method()
    
    # Assert
    assert result == expected_value
```

### BDD Test Example
Add to `features/*.feature`:
```gherkin
Scenario: New feature test
  Given some initial state
  When an action is performed
  Then the expected outcome occurs
```

### E2E Test Example
```python
def test_complete_workflow(client, auth_headers):
    """Test complete workflow"""
    # Make API calls
    response = client.post("/api/endpoint", headers=auth_headers)
    assert response.status_code == 200
```


