# 🚀 Start Here - Quick Setup

## ⚡ Fastest Way (No Docker Needed)

### Step 1: Start Backend (Terminal 1)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Step 2: Start Frontend (Terminal 2 - New PowerShell Window)

```powershell
cd frontend
npm install
npm run dev
```

Wait for: `Local: http://localhost:3000`

### Step 3: Open Browser

Go to: **http://localhost:3000**

That's it! The database (SQLite) will be created automatically.

---

## 🐳 Using Docker Instead?

1. **Start Docker Desktop** (from Start menu)
2. Wait for it to fully start (whale icon in system tray)
3. Run: `docker-compose up -d`

---

## ❓ Troubleshooting

**Backend won't start?**
- Make sure Python 3.11+ is installed
- Check if port 8000 is already in use

**Frontend won't start?**
- Make sure Node.js 18+ is installed
- Try: `npm install` again

**Database errors?**
- SQLite file will be created automatically in `backend/schafkopf.db`
- No setup needed!


