from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from .database import init_db
from .routers import base, events, projects


# --- 1. 生命周期 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 [System] 正在初始化数据库环境...")
    init_db()
    print("✅ [System] 数据库初始化完成")

    yield

    print("🛑 [System] 服务正在关闭...")


# --- 2. 实例化 FastAPI ---
app = FastAPI(
    title="Calendori API",
    description="Bang Dream Live Event Calendar Backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(base.router)
app.include_router(events.router)
app.include_router(projects.router)


if __name__ == "__main__":

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
