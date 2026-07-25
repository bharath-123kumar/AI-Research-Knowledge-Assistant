import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from config.settings import settings
from routes.document_routes import router as document_router
from routes.search_routes import router as search_router
from routes.analysis_routes import router as analysis_router
from routes.analytics_routes import router as analytics_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Enterprise-grade AI Research & Knowledge Assistant Backend with RAG, Page Citations, Hybrid Search & TensorFlow Document Classification.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register API Routers
app.include_router(document_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(analysis_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)

# Serve Static Web UI Dashboard
static_dir = os.path.join(settings.BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_ui():
        return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
