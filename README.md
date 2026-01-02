# Schafkopf Game

A cross-platform implementation of the traditional German card game Schafkopf, built with React (web), React Native (mobile), and Python FastAPI (backend).

## Features

- Full Schafkopf game implementation with all contract types (Rufer, Wenz, Solo)
- Complete scoring system (Schneider, Schwarz)
- **Real-time multiplayer** with WebSocket support (4 players)
- **Game room system** - create/join rooms, ready up, and start games
- Interactive tutorial
- **User authentication** with JWT tokens
- **User-specific statistics** and game history
- **Professional UI** with authentic German card suit icons
- **Docker containerization** for easy deployment
- **PostgreSQL database** support for production
- Cross-platform: Browser, iOS, Android, Desktop (planned)

## Project Structure

```
schafkopf-game/
├── frontend/          # React web application
├── backend/           # FastAPI backend
├── mobile/            # React Native mobile app (Phase 5)
└── README.md
```

## Getting Started

**No PostgreSQL installation needed!** Choose one of these options:

### Option 1: Docker Compose (Recommended - No Setup)

Docker handles PostgreSQL automatically. Just run:

```bash
docker-compose up -d
```

Access at http://localhost:3000

See below for detailed instructions.

### Option 2: Quick Local Development (SQLite)

No database setup needed - uses SQLite automatically:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

See below for all options.

### Manual Setup (Advanced)

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export SECRET_KEY="your-secret-key"
export DATABASE_URL="sqlite:///./schafkopf.db"  # or PostgreSQL URL
```

5. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Authentication

The app now includes secure user authentication:

- **Register**: Create a new account at `/login` (Register tab)
- **Login**: Authenticate with username and password
- **JWT Tokens**: Secure token-based authentication
- **User Stats**: Statistics are tied to user accounts

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment details.

## Game Rules

See the in-game tutorial for complete rules. Key points:

- 4 players, 32-card deck (German suits)
- Goal: Score at least 61 out of 120 points
- Three contract types: Rufer, Wenz, Solo
- Special scoring: Schneider (91+ points), Schwarz (all tricks)

## Development Status

- ✅ Phase 1: Browser MVP (Core Game)
- ✅ Phase 2: Full Game Rules
- ✅ Phase 3: Multiplayer & Backend (WebSocket - **COMPLETE**)
- ✅ Phase 4: Enhanced Features (Tutorial, Stats)
- 🚧 Phase 5: Mobile (iOS/Android) - Planned
- ⏳ Phase 6: Desktop (Electron) - Planned

## Technology Stack

- **Frontend:** React 18, TypeScript, Vite
- **Backend:** Python 3.11+, FastAPI, WebSockets
- **Mobile:** React Native (planned)
- **Database:** SQLite/PostgreSQL (for stats)

## Testing

### Backend Tests

```bash
cd backend
pip install -r requirements-test.txt
pytest tests/ -v -m "not e2e_docker"  # Fast tests (no Docker)
pytest tests/test_e2e_docker.py -v -m e2e_docker  # E2E tests (requires Docker)
```

### Frontend Tests

```bash
cd frontend
npm install
npm test -- --run
```

### Using Makefile

```bash
make test              # Run all backend tests (no Docker)
make test-e2e-docker   # Run E2E Docker tests
make test-frontend     # Run frontend tests
make test-all          # Run all tests including Docker E2E
make help              # See all available commands
```

## License

MIT

