from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.auth import router as auth_router
from app.api.rooms import router as rooms_router
from app.api.websocket import websocket_endpoint
from app.database.database import init_db
import os

app = FastAPI(title="Schafkopf Game API", version="0.1.0")

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Include routers
app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(rooms_router, prefix="/api")

@app.websocket("/ws/{game_id}")
async def websocket_route(websocket: WebSocket, game_id: str):
    """WebSocket endpoint - token should be passed as query parameter"""
    await websocket.accept()
    
    # Get token from query params
    query_params = dict(websocket.query_params)
    token = query_params.get("token", "")
    
    # Extract username from token (token uses username as "sub")
    username = "unknown"  # Default
    if token:
        try:
            from jose import jwt
            import os
            SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username = payload.get("sub", "unknown")
            if not username:
                await websocket.close(code=1008, reason="Invalid token")
                return
        except Exception as e:
            print(f"Token decode error: {e}")
            await websocket.close(code=1008, reason="Invalid token")
            return
    else:
        await websocket.close(code=1008, reason="No token provided")
        return
    
    user_id = username  # Use username as user_id since that's what's in the token
    
    await websocket_endpoint(websocket, game_id, user_id)

@app.get("/")
async def root():
    return {"message": "Schafkopf Game API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

