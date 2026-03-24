from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Import route modules (simplified skeleton)
from .api.routes import chat as chat_routes  # type: ignore
from .api.routes import health as health_routes  # type: ignore
from .api.routes import search as search_routes  # type: ignore

app = FastAPI(title="Local AI Agent MVP")

app.include_router(health_routes.router, prefix="/health")
app.include_router(chat_routes.router, prefix="/api")
app.include_router(search_routes.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok"}
