from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import init_db
from app.routers import auth, jobs, resumes, applications

app = FastAPI(title="ATS Resume-Job Matching Engine")

# CORS is wide-open here because this is a local-dev/portfolio project
# served from the same origin as its own frontend. In a real production
# system, allow_origins would be locked down to the actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(applications.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api")
def api_status():
    return {"status": "ok", "service": "ats-matching-engine"}


# Serves app/static/index.html at "/" — the simple UI on top of the API.
static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
