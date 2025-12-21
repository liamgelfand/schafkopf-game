# Quick Start Guide

## Option 1: Docker Compose (Easiest - No Local Setup Needed)

**No PostgreSQL installation required!** Docker will handle everything.

### Steps:

1. **Make sure Docker is installed:**
   - Download Docker Desktop: https://www.docker.com/products/docker-desktop
   - Start Docker Desktop

2. **Copy environment file (optional, has defaults):**
   ```bash
   cp .env.example .env
   ```

3. **Start everything:**
   ```bash
   docker-compose up -d
   ```
   
   This will:
   - Download and start PostgreSQL in a container
   - Build and start the backend
   - Build and start the frontend
   - Set up all networking automatically

4. **Check if it's running:**
   ```bash
   docker-compose ps
   ```

5. **View logs:**
   ```bash
   docker-compose logs -f
   ```

6. **Access the app:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

7. **Stop everything:**
   ```bash
   docker-compose down
   ```

8. **Stop and remove data (fresh start):**
   ```bash
   docker-compose down -v
   ```

---

## Option 2: Manual Setup (SQLite - No Database Setup Needed)

**Perfect for quick testing!** Uses SQLite (file-based database, no server needed).

### Backend:

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run backend (uses SQLite by default):**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The database file `schafkopf.db` will be created automatically in the backend folder.

### Frontend:

1. **Open a new terminal, navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start frontend:**
   ```bash
   npm run dev
   ```

4. **Access the app:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

---

## Option 3: Manual Setup with Local PostgreSQL

**Only if you want to test with PostgreSQL locally.**

### Install PostgreSQL:

- **Windows:** Download from https://www.postgresql.org/download/windows/
- **Mac:** `brew install postgresql@15` or download from postgresql.org
- **Linux:** `sudo apt-get install postgresql` (Ubuntu/Debian)

### Setup:

1. **Create database:**
   ```bash
   createdb schafkopf
   # Or using psql:
   psql -U postgres
   CREATE DATABASE schafkopf;
   \q
   ```

2. **Set environment variable:**
   ```bash
   # Windows (PowerShell):
   $env:DATABASE_URL="postgresql://username:password@localhost:5432/schafkopf"
   
   # Mac/Linux:
   export DATABASE_URL="postgresql://username:password@localhost:5432/schafkopf"
   ```

3. **Run backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

---

## Which Option Should I Use?

- **Option 1 (Docker):** Best for production-like testing, no local setup
- **Option 2 (SQLite):** Fastest for development, no database setup
- **Option 3 (Local PostgreSQL):** Only if you specifically need to test PostgreSQL features

**Recommendation:** Start with **Option 2** for quick testing, or **Option 1** if you want the full production setup.


