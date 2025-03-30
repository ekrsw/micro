from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db

app = FastAPI(
    title="Auth Service API",
    description="認証サービスAPI",
    version="0.1.0",
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの登録
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Auth Service API"}

@app.get("/health")
async def health_check():
    from app.db.db import SessionLocal
    from sqlalchemy import text
    
    # データベース接続の確認
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    finally:
        db.close()
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": "0.1.0"
    }

@app.on_event("startup")
async def startup_event():
    init_db()
